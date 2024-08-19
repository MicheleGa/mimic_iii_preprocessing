import os
from pathlib import Path
import shutil
import glob
from joblib import Parallel, delayed
import multiprocessing
from shutil import rmtree
from typing import Tuple
import wfdb
import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.signal import find_peaks


def count_patients_and_records(valid_segments_file: str) -> Tuple[int, int]:
    r"""
    Given a txt file with the database name and its valid segments, return the amount of different patients and 
    total number of reocords with the required signals specified during the data provisioning step.
    
    Parameters:
    ------------

    valid_segments_file: string,
        the txt file to be analyzed

    Returns:
    ------------

    An integer, the number of different patients 
    """
    
    with open(valid_segments_file, 'r') as seg_file:
        lines = seg_file.readlines()

        # First line is the database name
        _ = lines[0]
        patients = set()

        # Next lines are all structured as parent_directory/patient_id/segments
        for i in range(1, len(lines)):
            patients.add(lines[i].split('/')[1])
        
    return len(patients), len(lines) - 1


def nans_percentage(signal : np.array) -> float:
    r"""
    Not a Numbers percentage calculation.

    Parameters:
    ------------

    signal: np.array,
        the signal to analyze

    Returns:
    ------------

    The percentage of NaNs in the signal
    """
    return np.isnan(signal).astype("int").sum() / len(signal)
 

def flat_lines_detection(signal : np.array, delta : float = 1e-5, window_len = 3) -> float:
    r"""
    Flat lines detection.
    A flat part of the signal is defined as sig\[i\] = sig\[i\+1] &plusmn; &#916;.
    Return the percentage of flat lines

    Parameters:
    ------------

    signal: np.array,
        the signal to analyze
    delta: float, default 1e-5,
        the threshold to determine whether two values are equal
    window_len: int, default 3,
        the length of the window to compare consecutive values

    Returns:
    ------------

    the percentage of flat lines in the signal
    """

    # Efficient difference calculation using vectorization
    abs_diff = np.abs(signal[:-window_len] - signal[window_len:])

    # Flat line detection using comparison with threshold
    flat_locs_sig = abs_diff < delta

    # Handling initial window (vectorized using concatenate)
    pre_window = np.zeros(window_len, dtype=bool)

    return np.concatenate((pre_window, flat_locs_sig))


def interpolate_nan_pchip(data):
    r"""
    Interpolates NaN values in a 1D NumPy array using PCHIP.

    Parameters:
    ------------
    
    data: np.array, 
        the input 1D NumPy array.

    Returns:
    ------------
    
    The interpolated array.
    """

    valid_indices = np.where(~np.isnan(data))[0]
    invalid_indices = np.where(np.isnan(data))[0]

    # There is a paper suggesting this interpolation whihch better preserve frequencies
    interpolator = PchipInterpolator(valid_indices, data[valid_indices])
    interpolated_values = interpolator(invalid_indices)

    data[invalid_indices] = interpolated_values
    return data


def create_windows(win_len, fs, n_samp, overlap)-> Tuple[np.array, np.array]:
    r"""
    Function from https://github.com/Fabian-Sc85/non-invasive-bp-estimation-using-deep-learning/blob/main/prepare_MIMIC_dataset.py
    Intended to generate the start and end indexes of each window sliding over the signal for preprocessing.

    Parameters:
    ------------
    
    win_len: int, 
        length of a window in seconds
    fs: int, 
        sampling frequency of the signal
    n_samp: int,
        length of the signal
    overlap: float,
        percentage of overlap between adjacent windows

    Returns:
    ------------
    
    idx_start: np.array,
        array of window starting indexes in the signal
    idx_stop: np.array,
        array of window ending indexes in the signal.  
    """
    
    win_len = win_len * fs
    overlap = np.round(overlap * win_len)
    n_samp = n_samp - win_len + 1

    idx_start = np.round(np.arange(0, n_samp, win_len - overlap)).astype(int)
    idx_stop = np.round(idx_start + win_len - 1)

    return idx_start, idx_stop


def save_records_worker_function(database_name : str, valid_segment_path : str, output_dir : str, valid_bp_ranges : dict, thresholds : dict, windowing_param : dict) -> None:
    r"""
    A thead wil spawn executing the code of this function, that is 
    downloading, performing intial preprocessing, and storing of the signals.

    Parameters:
    ------------

    database_name: str,
        the name of the dataset, it will be used to build the file path
    valid_segment_path: str,
        path identifying the subject's segment inside the dataset
    output_dir: str,
        the root directory where to save the signals
    valid_bp_ranges: dict,
        the upper and lower valid values for systolic and diastolic blood pressure
    thresholds: dict,
        contains the permitted % of anomalies in the signals (NaNs and flat parts)
    windowing_param: dict,
        contains parameters tos etup the sliding window (length in seconds and overlap)
    
    Returns:
    ------------
    None
    """
    print(f'Processing {valid_segment_path[:-1]}', flush=True)

    # Retrieve segment information from the txt file line
    parent_folder, patient_id, seg_id = valid_segment_path.split('/')
    seg_id = seg_id.strip() # remove the initial/endline whitespaces

    record_data = wfdb.rdrecord(record_name=seg_id, pn_dir=f'{database_name}/{parent_folder}/{patient_id}')

    # Note: we are sure that segments have ABP or PLETH thanks to the data provisioning step
    abp_idx = record_data.sig_name.index('ABP')
    ppg_idx = record_data.sig_name.index('PLETH')

    abp = record_data.p_signal[:, abp_idx]
    ppg = record_data.p_signal[:, ppg_idx]
    fs = record_data.fs

    # Do not save signals with more then 5% of NaNs
    if nans_percentage(abp) <= thresholds['nans_th'] and nans_percentage(ppg) < thresholds['nans_th']:
        
        # Interpolate to remove nan
        abp = interpolate_nan_pchip(abp)
        ppg = interpolate_nan_pchip(ppg)
     
        # Do not save signals with more then 5% of flats
        abp_per_flat = len(np.where(flat_lines_detection(abp))[0]) / len(abp)
        ppg_per_flat = len(np.where(flat_lines_detection(ppg))[0]) / len(ppg)

        if abp_per_flat <= thresholds['flat_th'] and ppg_per_flat < thresholds['flat_th']:

            n_samples = len(abp)
            win_start, win_stop = create_windows(windowing_param['win_len'], fs, n_samples, windowing_param['win_overlap'])
            n_win = len(win_start)
            
            SBP = []
            DBP = []
            
            # Sliding window over the signal: it prevents to remove signals with small amount of missing data 
            for j in range(0, n_win):
                idx_start = win_start[j]
                idx_stop = win_stop[j]

                sig = abp[idx_start : idx_stop]
                
                try:
                    # Interp to remove nan: can raise an exception if the window is completely empty
                    sig = interpolate_nan_pchip(sig)

                    # scipy.signal.find_peaks return a pair with idxs on the first element
                    peaks = find_peaks(sig)[0]
                    valleys = find_peaks(-sig)[0]

                    # Check in case there signal is basically flat in the window
                    if len(peaks) == 0 or len(valleys) == 0:
                        # Set an invalid BP value
                        sbp = 0.0
                        dbp = 0.0
                    else:
                        # Calculate the actual SBP and DBP
                        sbp = np.mean(sig[peaks])
                        dbp = np.mean(sig[valleys])

                    SBP.append(sbp)
                    DBP.append(dbp)

                except: 
                    SBP.append(0.0)
                    DBP.append(0.0)        

            # Calculate the overall DBP and SBP for the whole signal
            SBP = np.array(SBP).mean()
            DBP = np.array(DBP).mean()

            # Do not save signals with abnormal BP values
            if SBP >= valid_bp_ranges['low_sbp'] and SBP <= valid_bp_ranges['up_sbp'] and DBP >= valid_bp_ranges['low_dbp'] and DBP <= valid_bp_ranges['up_dbp']:
                
                # Save valid segments
                output_path = Path(os.path.join(f'{output_dir}/{parent_folder}/{patient_id}/{seg_id}'))

                if output_path.exists():
                    rmtree(output_path)
                os.makedirs(output_path)

                np.save(os.path.join(output_path, 'abp'), abp)
                np.save(os.path.join(output_path, 'ppg'), ppg)
                print(f'Saved {output_path}', flush=True)
            
            else:
                print(f'ABP with invalid ranges for {valid_segment_path[:-1]} ...')    
        
        else:
            print(f'Too many flat parts for {valid_segment_path[:-1]} ...')
        
    else:
        print(f'Too many NaNs for {valid_segment_path[:-1]} ...')

        

def download_mimic_iii_records(valid_segments_file_path, output_dir, valid_BP_ranges, thresholds, windowing_param, n_cores : int = 1) -> None:
    r"""
    This function downloads the valid segments containing the required signals and with the specified minimum length.
    After the downloads, signals are processed to look for NaNs, flat lines, and valid BP ranges. 
    If a signal pass the checks, then it is stored locally.

    Parameters:
    ------------

    valid_segment_path: str,
        path identifying the subject's segment inside the dataset
    output_dir: str,
        root directory where to store signals 
    valid_bp_ranges: dict,
        the upper and lower valid values for systolic and diastolic blood pressure
    thresholds: dict,
        contains the permitted % of anomalies in the signals (NaNs and flat parts)
    windowing_param: dict,
        contains parameters tos etup the sliding window (length in seconds and overlap)
    n_cores: int, default 1,
        number of parallel cores to use
    
    Returns:
    ------------
    None
    """ 

    # Create patients directory
    output_dir = os.path.join(output_dir, 'records')
    os.makedirs(output_dir, exist_ok=True)

    # Parallel cores
    num_cores = multiprocessing.cpu_count()
    used_cores = n_cores
    print(f'Using {used_cores}/{num_cores} cores')

    with open(valid_segments_file_path, 'r') as seg_file:
        lines = seg_file.readlines()

        # First line is the database name
        database_name = lines[0].strip() # remove the endline \n char

        # Loop through the valid segments
        Parallel(n_jobs=used_cores)(delayed(save_records_worker_function)(database_name, lines[i], output_dir, valid_BP_ranges, thresholds, windowing_param) for i in range(7915, 50779)) 