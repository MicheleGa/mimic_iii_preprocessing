import multiprocessing
import os
from pathlib import Path
from shutil import rmtree
from joblib import Parallel, delayed
import wfdb
import numpy as np


def worker_function(segment_path, output_dir) -> None:
    segment_path = segment_path.strip()
    print(f'Downloading {segment_path.strip()} ...', flush=True)
    parent_folder, patient_id, seg_id = segment_path.split('/')[-3:]
    record_data = wfdb.rdrecord(record_name=seg_id.strip(), pn_dir=f'mimic3wdb-matched/1.0/{parent_folder}/{patient_id}')
    abp_idx = record_data.sig_name.index('ABP')
    ppg_idx = record_data.sig_name.index('PLETH')
 
    abp = record_data.p_signal[:, abp_idx]
    ppg = record_data.p_signal[:, ppg_idx]

    output_path = os.path.join(output_dir, segment_path)

    if Path(output_path).exists():
        rmtree(output_path)
    os.makedirs(output_path)

    np.save(os.path.join(output_path, 'abp'), abp)
    np.save(os.path.join(output_path, 'ppg'), ppg)
    print(f'Saved {output_path}', flush=True)



missing_segments_to_download_file_path = '../output/logs/segments_preprocessing/downloaded preprocessed_segs.txt' 
output_dir = '../output/records/'


# Parallel cores
num_cores = multiprocessing.cpu_count()
used_cores = 12
print(f'Using {used_cores}/{num_cores} cores')

with open(missing_segments_to_download_file_path, 'r') as f1:
    lines = f1.readlines()

    Parallel(n_jobs=used_cores)(delayed(worker_function)(lines[i], output_dir) for i in range(len(lines))) 