with open("./output/logs/valid_segment_download_win_0.log", 'rb') as f:
    raw_data = f.read()
normalized_data = raw_data.replace(b'\r\n', b'\n')
# Try different encodings based on your knowledge or guesses
encodings_to_try = ['utf-8', 'latin1', 'windows-1252', 'cp1251']

for encoding in encodings_to_try:
    try:
        decoded_data = normalized_data.decode(encoding)
        
        with open("./output/logs/valid_segment_download_win_0.log", 'w') as f:
            f.write(decoded_data)
        print(f"Successfully decoded and re-encoded using {encoding}")
        break
    except UnicodeDecodeError:
        print(f"Decoding failed with {encoding}")