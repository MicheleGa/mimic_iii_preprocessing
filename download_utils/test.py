import os
import glob
import zipfile
from concurrent.futures import ThreadPoolExecutor


downloaded_segs = []
with open('./output/actually_downloaded_segments.txt', 'r') as f1:
    downloaded_segs.extend(f1.readlines())

for i in range(len(downloaded_segs)):
    downloaded_segs[i] = downloaded_segs[i].strip()

downloaded_segs_2 = []
with open('./output/downloaded_segments.txt', 'r') as f1:
    downloaded_segs_2.extend(f1.readlines())


for i in range(len(downloaded_segs_2)):
    downloaded_segs_2[i] = downloaded_segs_2[i].strip()

missing_seg = []
for el in downloaded_segs:
    if el not in downloaded_segs_2:
        missing_seg.append(el)

for el in missing_seg:
    print(el)   
'''
zip_file_paths = ['./output/records/p07.zip', './output/records/p09.zip']

# unzip a file from an archive
def unzip_file(handle, filename, path):
    # unzip the file
    handle.extract(filename, path)
    # report progress
    print(f'.unzipped {filename}')

for zip_file_path in zip_file_paths: 

    print(f'Extracting {zip_file_path} ...')

    with zipfile.ZipFile(zip_file_path, 'r') as handle:
        # start the thread pool
        with ThreadPoolExecutor(100) as exe:
            # unzip each file from the archive
            _ = [exe.submit(unzip_file, handle, m, './output/records/') for m in handle.namelist()]

    os.remove(zip_file_path)
'''