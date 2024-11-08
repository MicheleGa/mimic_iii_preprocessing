# MIMIC III Preprocessing Pipeline

The code in this repository is inteded to develop a bewnchmark of Continual Learning mwethods for Physiological Signals Analysis.
The different ML pipeline step will be developed:

>- data provisiong
>- data processing
>- data visualization.

In *requirements.txt* the list of Python packages required to run the code is provided.
It is highly recommended to first create a virtualenv (in the local repository) with

```bash
python3.10 -m venv venv
source venv/bin/activate
```

and then to install the dependecies with

```bash
pip install -r requirements.txt
```

## General Useful Commands

To check if somebody else is using te HPC machine use

```bash
pipx run nvitop
```

from [here](https://github.com/XuehaiPan/nvitop).

Instead, another useful command can be running the program in a detached thread form the shell, so that if the connection to the HPC machine is closed, then the program can continue working:

```bash
mkdir /location/of/the/output
nohup ./your_script_runner.sh > /location/of/the/output/file.log 2>&1 &
```

## Data Provsioning

It is intended to retrieve waveforms from [MIMIC-III Waveform Database Matched Subset](https://physionet.org/content/mimic3wdb-matched/1.0/).
Specifically, it filters out patients who do not have required signals.
Since the connection to the dataset is a bit slow as it is stored in MIT servers in the USA, we can try to speed up the process with Python parallel libraries (not so much effective).
The code is develop starting from the [MIMIC WFDB tutorials repository](https://github.com/wfdb/mimic_wfdb_tutorials/tree/main).

To start the data provisioning process, run the *main.py*, it will use function inside the *data_provisioning.py*.

As a result of this part a txt file with valid segment is produced. A valid segment lasts at least 8 minute (length decided after this [paper](https://ieeexplore.ieee.org/document/9082808)) and contains both the arterial blood presure and the photoplethysmography signals.

## Data Preprocessing

Once the valid segments paths have been recorded in a txt file, we will download them in local using the *download_mimic_iii_records* function in *data_preprocessing.py*.
It exploits the Joblib python library to speed up the download process as the connection to the MIMIC-III server was slow. 
The downloads is followed by a preliminary preprocessing consisting of NaNs removal, segment with too many flat parts are discarde, segment with invalid ABP ranges are removed. Specifically, the average SBP/DBP are calcualted with a sliding window, when the average of SBPs/DBPs calculated in each window exceed some thresholds decided from papers. The line *mimic3wdb-matched/1.0* has been added to the *downloaded_segments.txt* file to make it consistent with the *valid_segments_retrieval.txt* file

After this step, downloaded files are zipped to save storage as they were not fitting inside this laptop.
The preprocessing proceed by unzipping the subfolders and analyzing its content before saving it.
This analysis aims to further remove signals that even after the interpolation of the ABP signal, present values outside the valid thresholds. In this case, no sliding window is considered, basically, the whole signal is interpolated and the max and min values of the signal are checked: if they are outside the provided values, then they are discarded. After this part, segments are saved physically in the device and not zipped. Hoping they will fit.

p08 had a directory with ppg and no abp.

total size 61,6 GB
