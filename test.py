import glob

with open('./output/valid_segments_pleth_abp_8m.txt','r') as f:
    lines = f.readlines()

    # First line is the database name
    database_name = lines[0][:-1] # remove the endline \n char

    segments_to_download = [lines[x][:-1] for x in range(12127, 18271)]
    
    downloaded_segs = glob.glob('./output/records/p00/*/*')
    downloaded_segs.extend(glob.glob('./output/records/p04/*/*'))

    print('Segments to download:', len(segments_to_download))
    print('Downloaded segments:', len(downloaded_segs))
    print()

    for i in range(len(downloaded_segs)):
        downloaded_segs[i] = '/'.join(downloaded_segs[i].split('/')[-3:])
    
    downloaded_segs = set(downloaded_segs)
    
    for el in set(segments_to_download):
        if el not in downloaded_segs:
            print('Missing segment:', el)    
    
    
    for line in range(1, len(lines)):
        
        if lines[line][:-1] == 'p04/p040000/3506991_0001':
            print(line)