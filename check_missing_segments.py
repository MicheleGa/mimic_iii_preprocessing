import glob

downloaded_segments = []

# Remember to change the log file to check !!!
with open('./output/logs/valid_segment_download_1.log','r') as f:
    downloaded_segments.extend(f.readlines())

# A segment that has been fully processed appear two times in the valid_segments_download.log file

with open('./output/valid_segments_pleth_abp_8m.txt','r') as f:
    lines = f.readlines()

    # First line is the database name
    database_name = lines[0][:-1] # remove the endline \n char

    # Look into valid_segment_download.log to get the last seegment whose processing has started and thus (probably) not finished
    # Reuse this part of code to get the index of the first missing sample
    for line in range(1, len(lines)):
        
        if lines[line][:-1] == 'p01/p011018/3195243_0010':
            print(line)
    exit()
    # Get the index and obtain the list of valid segment that had to be processed until this idx in valid_segments_pleth_abp_8m.txt 
    segments_to_download = [lines[x][:-1] for x in range(1, 2270)]
    missing_segments = []
    for seg in segments_to_download:
        count = 0
        for el in downloaded_segments:
            if seg in el:
                count = count + 1
        if count == 1:
            print(f'Missing {seg}')
            missing_segments.append(seg)
            break
        elif count == 0:
            print(f'Still no processing for {seg}')
        elif count == 2:
            print(f'Processed {seg}')
        else:
            print(f'???')
    
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
    
    
    