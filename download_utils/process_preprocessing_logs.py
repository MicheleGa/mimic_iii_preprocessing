import os
import glob
import zipfile
from concurrent.futures import ThreadPoolExecutor


preprocessed_segs = []
with open('../output/logs/valid_segments_preprocess_2.log', 'r') as f1:
    preprocessed_segs.extend(f1.readlines())

with open('../output/logs/successfully preprocessed_segs.txt', 'a') as f1, open('../output/logs/removed preprocessed_segs.txt', 'a') as f2, open('../output/logs/downloaded preprocessed_segs.txt', 'a') as f3:
    for i in range(len(preprocessed_segs)):
        seg = preprocessed_segs[i].strip()
        if 'Saved' in seg:
            f1.write(f'{seg[23:]}\n')
        elif 'Removed' in seg:
            f2.write(f'{seg[25:]}\n')
        elif 'Downloading' in seg:
            f3.write(f'{seg[29:-4]}\n')
        else:
            continue