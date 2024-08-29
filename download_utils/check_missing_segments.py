import os
import glob

from numpy import sort

downloaded_segments = []

intial_valid_segments_path = os.path.join('./output', 'valid_segments_pleth_abp_8m.txt')
valid_downloaded_segments_path = sort(glob.glob('./output/logs/valid_segment_download_*')) # sort it is important to maintain the order of downloads


def get_idx(li, el_to_find) -> int:
    idx = -1
    for i in range(len(li)):
        # strip to remove the \n char
        if li[i].strip() == el_to_find:
            idx = i
    return idx

for log_file in valid_downloaded_segments_path:
    # Remember to change the log file to check !!!
    try:
        with open(log_file, 'r') as f:
            downloaded_segments.extend(f.readlines())
    except UnicodeDecodeError:
        with open(log_file, 'r', encoding='utf-16') as f:
            downloaded_segments.extend(f.readlines())

# A segment that has been fully processed appear two times in the valid_segments_download.log file
with open(intial_valid_segments_path, 'r') as f:
    lines = f.readlines()

    # First line is the database name
    database_name = lines[0][:-1] # remove the endline \n char

    # Look into valid_segment_download.log to get the last seegment whose processing has started and thus (probably) not finished
    #last_processed_idx = get_idx(lines, lines[-1])
   
    # Get the index and obtain the list of valid segment that had to be processed until this idx in valid_segments_pleth_abp_8m.txt 
    segments_to_download = [lines[x].strip() for x in range(1, len(lines))]

    missing_segments = []
    actually_downloaded_segments = []
    strange_segments = []
    deleted_segments = []
    
    for seg in segments_to_download:
        count = 0
        for el in downloaded_segments:
            if (seg in el) and ('Processing' in el) and (count == 0):
                count = 1
            elif (seg in el) and ('Saved' in el) and (count == 1):
                count = 2
            elif (seg in el) and ('flat' in el) and (count == 1):
                count = 3
            elif (seg in el) and ('NaNs' in el) and (count == 1):
                count = 4
            elif (seg in el) and ('ABP' in el) and (count == 1):
                count = 5
            else:
                continue
        
        if count == 0:
            strange_segments.append(seg)
        elif count == 1:
            missing_segments.append(seg)
        elif count == 2:
            actually_downloaded_segments.append(seg)
        else:
            deleted_segments.append(seg)
    
    with open('./output/strange_segments.txt', 'w') as f:
        for el in strange_segments:
            f.write(f"{el}\n")

    with open('./output/missing_segments.txt', 'w') as f:
        for el in missing_segments:
            f.write(f"{el}\n")

    with open('./output/actually_downloaded_segments.txt', 'w') as f:
        for el in actually_downloaded_segments:
            f.write(f"{el}\n")
    
    with open('./output/deleted_segments.txt', 'w') as f:
        for el in deleted_segments:
            f.write(f"{el}\n")
    
    
#    downloaded_segs = glob.glob('./output/records/p00/*/*')
#    downloaded_segs.extend(glob.glob('./output/records/p04/*/*'))

#    print('Segments to download:', len(segments_to_download))
#    print('Downloaded segments:', len(downloaded_segs))
#    print()

#    for i in range(len(downloaded_segs)):
#        downloaded_segs[i] = '/'.join(downloaded_segs[i].split('/')[-3:])
    
#    downloaded_segs = set(downloaded_segs)
    
#    for el in set(segments_to_download):
#        if el not in downloaded_segs:
#            print('Missing segment:', el)    
