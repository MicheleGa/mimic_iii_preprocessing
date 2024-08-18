import os

downloaded_segments = []

valid_downloaded_segments_path = os.path.join('./output', 'logs', 'valid_segment_download_win_0.txt')
already_downloaded_segments_path = os.path.join('./output', 'downloaded_segments.txt')

# Remember to change the log file to check !!!
with open(valid_downloaded_segments_path,'r') as f:
    lines = f.readlines()

    for line in lines:
        if 'Saved' in line:
            downloaded_segments.append(line)

already_downloaded_segments = []
with open(already_downloaded_segments_path, 'r') as f:
    already_downloaded_segments.extend(f.readlines())

# append mode
with open(already_downloaded_segments_path, 'a') as f:
    for seg in downloaded_segments:
        if seg not in already_downloaded_segments:
            f.writelines(seg)