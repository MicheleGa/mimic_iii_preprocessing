import os
from joblib import Parallel, delayed
import multiprocessing
import numpy as np
from matplotlib import pyplot as plt
import wfdb
from scipy.signal import welch


def plot_psd(signal : np.array, sampling_rate : int, window : str = 'hann'):
    r"""
    Plots the power spectral density with the first harmonic of a signal.

    Parameters:
    ------------
    signal: np.array,
        The input signal as a numpy array.
    sampling_rate: int,
        The sampling rate of the signal.
    window: str, default hanning window,
        The windowing function to apply (optional).

    Returns:
    ------------
    None
    """

    # Calculate PSD
    f, Pxx_den = welch(signal, fs=sampling_rate, window=window)
    plt.figure()
    plt.semilogy(f, Pxx_den, color='b')
    plt.xlabel('frequency [Hz]')
    plt.ylabel('PSD [V**2/Hz]')

    # Find the peak frequency (first harmonic)
    first_harmonic = f[np.argmax(Pxx_den)]
    plt.axvline(x=first_harmonic, color='r', linestyle='--', label='First Harmonic')
    plt.legend()
    plt.show()
    plt.clf()


def worker_function(database_name : str, seg_path : str, output_dir : str) -> None:
    r"""
    A thead wil spawn executing the code of this function, that is:
    - querying the database for the specific segment associated to a patient
    - extracting the PPG and ABP signals
    - plotting and saving the signals in a figure

    Parameters:
    ------------

    database_name: string,
        the name of the dataset, it will be used to build the file path
    seg_path: string,
        path identifying the subject segmetn inside the dataset
    output_dir: string,
        the location where the images will be saved
        
    Returns:
    ------------
    None
    """

    # The seg_path is stored inside a txt file in the follwing format 'parent_folder/patient_id/seg_id'
    parent_folder, patient_id, seg_id = seg_path.split('/')
    seg_id = seg_id[:-1] # remove the endline \n char 
    
    record_data = wfdb.rdrecord(record_name=seg_id, pn_dir=f'{database_name}/{parent_folder}/{patient_id}')
    fs = record_data.fs

    abp_idx = record_data.sig_name.index('ABP')
    ppg_idx = record_data.sig_name.index('PLETH')

    abp = record_data.p_signal[:, abp_idx]
    ppg = record_data.p_signal[:, ppg_idx]

    t = np.arange(0, (len(abp) / fs), 1.0 / fs)

    plt.title('Arterial Blood Pressure')
    plt.xlabel('s')
    plt.ylabel(record_data.units[abp_idx])
    plt.plot(t, abp, color='orange', label='ABP')
    plt.savefig(os.path.join(output_dir, f'{patient_id}_{seg_id}_ABP.png'))
    plt.clf()

    plt.title('PhotoPlethysmoGraphy')
    plt.xlabel('s')
    plt.ylabel(record_data.units[ppg_idx])
    plt.plot(t, ppg, color='blue', label='PPG')
    plt.savefig(os.path.join(output_dir, f'{patient_id}_{seg_id}_PPG.png'))
    plt.clf()



def save_abp_and_ppg_figures(valid_segment_file : str, output_dir : str, n_sample_to_plot : int = 4, n_cores : int = 1) -> None:
    r"""
    The following function creates the directories required to save the figures associated to the physiological signal of a patient,
    and then it queries the dataset for the specifc patients' segments. The required information is stored in a txt file produced from the data provisioning step.

    Parameters:
    ------------
    valid_segment_file: string,
        the txt file contaning the database name as first line and the valid segments information as the rest of the file
    output_dir: string,
        the parent directory where to save the output figures
    n_sample_to_plot: int, default 4,
        the number of patients to analyze
    n_cores: int, default 1,
        the number of cores to use to speed up the data retrieval process
        
    Returns:
    ------------
    None
    """
    
    output_dir = os.path.join(output_dir, 'figs')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Parallel cores
    num_cores = multiprocessing.cpu_count()
    used_cores = n_cores
    print(f'Used cores {used_cores}/{num_cores}')
    
    with open(valid_segment_file, 'r') as seg_file:
        lines = seg_file.readlines()

        # First line is the database name 
        database_name = lines[0][:-1] # remove the endline \n char

        # Next lines are all structured as parent_directory/patient_id/segments
        _ = Parallel(n_jobs=used_cores)(delayed(worker_function)(database_name, lines[i], output_dir) for i in range(1, n_sample_to_plot))

  
def plot_signal(signal : np.array, fs : int, flat_locs_sig : np.array = None, peaks : np.array = None, valleys: np.array = None, title : str = '', save_path : str = './') -> None:
    r"""
    Handy function to plot a signal, with its peaks, valleys, flat parts, outliers, and lower/upper envelops (when provided).

    Parameters:
    ------------

    signal: np.array,
        the signal to analyze
    fs: int,
        the sampling rate of the signal
    flat_locs_sig: np.array, default None,
        the locations of the flat lines
    peaks: np.array, default None,
        the locations of the peaks
    valleys: np.array, default None,
        the locations of the valleys
    title: str, default '',
        the title of the plot
    save_path: str, default './',
        where to save the image

    Returns:
    ------------
    None
    """

    # Seconds on the x-axis, amplitude on the y-axis
    t = np.arange(0, (len(signal) / fs), 1.0 / fs)
    plt.title(f'{title}')
    plt.xlabel('s')
    plt.plot(t, signal, color='black', label='signal')

    if peaks is not None:
        # If peaks are provided, then also the upper envelope of the signal is plotted
        x_vals = np.arange(len(signal))
        up_env = np.interp(x_vals, peaks, signal[peaks])
        plt.plot(t, up_env, color='red', label='up envelope', marker='o', linestyle='dashed', linewidth=1, markersize=1)
        plt.scatter(t[peaks], signal[peaks], color='red', label='peaks')

    if valleys is not None:
        # If valleys are provided, then also the lower envelope of the signal is plotted
        x_vals = np.arange(len(signal))
        down_env = np.interp(x_vals, valleys, signal[valleys])
        plt.plot(t, down_env, color='blue', label='down envelope', marker='o', linestyle='dashed', linewidth=1, markersize=1)
        plt.scatter(t[valleys], signal[valleys], color='blue', label='valleys')

    if flat_locs_sig is not None:
        plt.scatter(t[flat_locs_sig], signal[flat_locs_sig], color='green', label='flat lines')

    plt.legend()
    plt.savefig(save_path)
    plt.clf()