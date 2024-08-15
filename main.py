import os
import argparse
from data_provisioning import valid_segments_retrieval
from data_preprocessing import count_patients_and_records, download_mimic_iii_records
from data_visualization import save_abp_and_ppg_figures

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Continual Learning for Physiological Signals Analysis Benchmark')
    
    # Backup dir
    parser.add_argument('--output_dir', nargs='?', type=str, help='location of the txt files produced during the pipeline', default='./output')
    # Output file name
    parser.add_argument('--output_file_name', nargs='?', type=str, help='name of the txt files that will be saved in the backup directory', default='valid_segments.txt')
    # MIMIC database name inside Physionet
    parser.add_argument('--database_name', nargs='?', type=str, help='the name of the database to process', default='mimic3wdb-matched/1.0')
    # Minimum segment duration (min)
    parser.add_argument('--min_duration', nargs='?', type=int, help='minimum signals duration in minutes', default=8)
    # NUmber of parallel cores to use
    parser.add_argument('--n_cores', nargs='?', type=int, help='number of parallel cores to use', default=10)
    
    args = parser.parse_args()

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    output_file = os.path.join(args.output_dir, args.output_file_name)

    # Look for segments of patients with these signals recorded simultaneously
    # These acronyms match the dataset format, so beware in changing them
    required_signals = set({'ABP', 'PLETH'})

    # Valid segments identifiers will be saved to output_file
    #valid_segments_file = valid_segments_retrieval(args.database_name, required_signals, args.min_duration, output_file, n_cores=8)

    valid_segments_file = os.path.join(args.output_dir, 'valid_segments_pleth_abp_8m.txt')

    num_patients, num_records = count_patients_and_records(valid_segments_file)

    print(f'There are {num_patients} different patients, for a total of {num_records} different records, from {args.database_name} with {str(required_signals)} that last at least {args.min_duration} m.')

    # Ranges decided empirically by looking at papers
    valid_BP_ranges = {
        'up_sbp' : 220.0,
        'low_sbp' : 60.0,
        'up_dbp' : 140.0,
        'low_dbp' : 30.0,
    }

    # Threshold taken from Non-invasive arterial blood pressure measurement and SpO2 estimation using PPG signal: a deep learning framework 
    thresholds = {
        'nans_th' : 0.05,
        'flat_th' : 0.05, 
    }

    windowing_param = {
        'win_len' : 20, # Parameters choose after Non-invasive arterial blood pressure measurement and SpO2 estimation using PPG signal: a deep learning framework 
        'win_overlap' : 0.5, # Parameter as in https://github.com/Fabian-Sc85/non-invasive-bp-estimation-using-deep-learning/blob/main/prepare_MIMIC_dataset.py
    }

    download_mimic_iii_records(valid_segments_file, args.output_dir, valid_BP_ranges, thresholds, windowing_param, n_cores=args.n_cores)

    


    
