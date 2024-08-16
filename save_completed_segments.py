downloaded_segments = []

# Remember to change the log file to check !!!
with open('./output/logs/valid_segment_download_1.log','r') as f:
    lines = f.readlines()

    for line in lines:
        if 'Saved' in line:
            downloaded_segments.append(line)

already_downloaded_segments = []
with open('./output/downloaded_segments.txt', 'r') as f:
    already_downloaded_segments.extend(f.readlines())

# append mode
with open('./output/downloaded_segments.txt', 'a') as f:
    for seg in downloaded_segments:
        if seg not in already_downloaded_segments:
            f.writelines(seg)