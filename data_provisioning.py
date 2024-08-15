from pathlib import Path
import wfdb
from joblib import Parallel, delayed
import multiprocessing
from typing import Optional


def worker_function(subject_file: str, database_name: str, subject: str, subject_id: str, required_signals: set, min_duration: int) -> Optional[Path]:
  r"""
  A thead wil spawn executing the code of this function, that consist in:
  - checking if a file of a subject contains waveform data
  - checking if the waveform data has the required signals
  - checking if the waveform is long enough

  Parameters:
  ------------

  f: string,
    the file to be analyzed
  database_name: string,
    the name of the dataset, it will be used to build the file path
  subject: string,
    path identifying the subject inside the dataset
  subject_id: string,
    last part of the subject variable
  required_signal: set,
    which signals (arterial blood pressure, photoplethysmography, etc.) to look for
  min_duration: int,
    minimum length of a valid segment

  Returns:
  ------------
  A PosixPath that can be used later to retrieve the waveform data or None
  """

  # In the MIMIC III Matched Subset files starting with the subject_id are not waveforms
  if not subject_file.startswith(subject_id):

    try:
      # Query the dataset, this operation is slow due to connection
      # It can throw a 404, this is why it is in side a try-catch
      segment_header = wfdb.rdheader(record_name=subject_file, pn_dir=f'{database_name}/{subject}')
    except:
      print(f'No file found for {database_name}/{subject}/{subject_file}', flush=True)
      return None
    
    # Check for the required signals
    if required_signals.issubset(set(segment_header.sig_name)): # set inclusion ops are efficient
      sig_len_min = segment_header.sig_len / (segment_header.fs * 60)

      if sig_len_min >= min_duration:
        return Path(f'{subject}{subject_file}') # valid segment that has the required signals sand it is long enough
      else: 
        return None
    else:
      return None
  else:
    return None
  

def valid_segments_retrieval(database_name: str, required_signals: set, min_duration: int, output_file: str, n_cores : int = 1) -> str:
  r"""
  This function analyze the MIMIC-III Matched subset dataset, by examining the header files of patients
  who have the required signals. It is worth noticing that patients are organized in folders 
  (e.g. p017488 is inside folder p01) and each patient may have associated more visits to the hospital.
  Each visit have some files associated, among themthere are records of vital signs (ECG, Respiratory Rate, 
  Blood Pressure, PPG, etc.). These records are divided in segmentswhich may or may not contain the required signals. 
  Additionally, it removes segments that last less than 8 minutes.

  Parameters:
  ------------

  database_name: string,
    the name of the dataset, it will be used to build the file path
  required_signal: set,
    which signals (arterial blood pressure, photoplethysmography, etc.) to look for
  min_duration: int,
    minimum duration of a signal
  output_file: str,
    where to save the list of valid segments
  n_cores: int, default 1,
    number of parallel cores to use
  
  Returns:
  ------------
  output_file_new_path: str,
    the path to the txt file with valid segments location in the database
  """ 

  # Each subject may be associated with multiple records
  subjects = wfdb.get_record_list(database_name)
  print(f"The '{database_name}' database contains data from {len(subjects)} subjects")

  # Iterate the subjects to get a list of records
  records = []

  # Parallel cores
  num_cores = multiprocessing.cpu_count()
  used_cores = n_cores
  print(f'Using {used_cores}/{num_cores} cores')

  j=0
  for subject in subjects:
    # Retrieve the file associated to a patient
    # Thanks to wfdb we have to distinguish only between numerics and waveforms (layout files are not appearing,
    # print files to get evidence of this)
    files = wfdb.get_record_list(f'{database_name}/{subject}')

    # The subject id is needed to remove files associated to a study that are not waveforms
    subject_id = subject.split('/')[1]

    segments = Parallel(n_jobs=used_cores)(delayed(worker_function)(files[i], database_name, subject, subject_id, required_signals, min_duration) for i in range(len(files)))

    # Segments contains the results of the parallel execution
    records.extend([record for record in segments if record is not None])

    j += 1
    if j % 1000 == 0:
      print(f'Subjects processed {j}/{len(subjects)}')

  print()
  print(f"Loaded {len(records)} records from the '{database_name}' database.")

  # Save the list as a txt file
  output_file_new_path = output_file[:-4] # remove extension
  
  # Add requried signals to name
  for el in required_signals:
    output_file_new_path += '_' + str(el).lower()

  # Add duration (in minutes) to signal name
  output_file_new_path += '_' + str(min_duration) + 'm'
  output_file_new_path += '.txt'

  with open(output_file_new_path, 'w') as f:
    f.write(f"{database_name}\n")
    for record in records:
      f.write(f"{record}\n")

  return output_file_new_path
    