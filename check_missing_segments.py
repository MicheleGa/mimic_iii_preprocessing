import os
import glob

downloaded_segments = []

intial_valid_segments_path = os.path.join('./output', 'valid_segments_pleth_abp_8m.txt')
valid_downloaded_segments_path = os.path.join('./output', 'logs', 'valid_segment_download_2.log')


def get_idx(li, el_to_find) -> int:
    idx = -1
    for i in range(len(li)):
        # strip to remove the \n char
        if li[i].strip() == el_to_find:
            idx = i
    return idx


# Remember to change the log file to check !!!
with open(valid_downloaded_segments_path, 'r') as f:
    downloaded_segments.extend(f.readlines())

# A segment that has been fully processed appear two times in the valid_segments_download.log file

with open(intial_valid_segments_path, 'r') as f:
    lines = f.readlines()

    # First line is the database name
    database_name = lines[0][:-1] # remove the endline \n char

    # Look into valid_segment_download.log to get the last seegment whose processing has started and thus (probably) not finished
    last_processed_idx = get_idx(lines, 'p09/p091031/3032690_0087')
   
    # Get the index and obtain the list of valid segment that had to be processed until this idx in valid_segments_pleth_abp_8m.txt 
    segments_to_download = [lines[x].strip() for x in range(1, last_processed_idx)]
    missing_segments = []
    for seg in segments_to_download:
        count = 0
        for el in downloaded_segments:
            if seg in el:
                count = count + 1
        if count == 1:
            missing_segments.append(seg)
    
    for el in missing_segments:
        print(f'Missing {el} with idx {get_idx(lines, el)}')
    
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
    
    
    