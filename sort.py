import os
import sys
from PIL import Image

def main():
    ROOT = r'C:\Users\Scouter\Downloads'
    DUMP_PATH = rf'{ROOT}\image-dump'
    
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        DUMP_PATH = sys.argv[1]
        ROOT = DUMP_PATH + r'\..\sorted'
    
    BOARD = r''
    THREAD = r''
    SMALL_PATH = rf'{ROOT}\out\tiny'
    HD_PATH = rf'{ROOT}\out\1080'
    UHD_PATH = rf'{ROOT}\out\1440'
    FOURK_PATH = rf'{ROOT}\out\2160'
    TALL_PATH = rf'{ROOT}\out\tall'
    WIDE_PATH = rf'{ROOT}\out\wide'
    WEBM_PATH = rf'{ROOT}\out\webm'

    for path in (SMALL_PATH, HD_PATH, UHD_PATH, FOURK_PATH, TALL_PATH, WEBM_PATH, WIDE_PATH):
        if not os.path.exists(path):
            os.makedirs(path)

    for subdir, dirs, files in os.walk(rf'{DUMP_PATH}{BOARD}{THREAD}'):
        for file in files:
            curr_path = os.path.join(subdir, file)
            
            if str(file.split('.')[-1]).lower() in ['png', 'jpeg', 'jpg', 'bmp', 'gif']:
                im = Image.open(curr_path)
                x, y = im.size
                im.close()

                try:
                    # first check if too small
                    if (x < 1920) or (y < 1080):
                        os.replace(curr_path, os.path.join(SMALL_PATH, file))
                        print(f'TOO SMALL: {curr_path}')
                        continue

                    # then check if it is a vertical image
                    if y > x:
                        os.replace(curr_path, os.path.join(TALL_PATH, file))
                        print(f'VERTICAL: {curr_path}')
                        continue

                    # then check if it is extra wide
                    if x > y*2:
                        os.replace(curr_path, os.path.join(WIDE_PATH, file))
                        print(f'WIDE: {curr_path}')
                        continue

                    if (x >= 3840) and (y >= 2160):
                        os.replace(curr_path, os.path.join(FOURK_PATH, file))
                        print(f'>4K: {curr_path}')
                        continue

                    if (x >= 2560) and (y >= 1440):
                        os.replace(curr_path, os.path.join(UHD_PATH, file))
                        print(f'>2K: {curr_path}')
                        continue

                    if (x >= 1920) and (y >= 1080):
                        os.replace(curr_path, os.path.join(HD_PATH, file))
                        print(f'>1080: {curr_path}')
                        continue
                except:
                    print(f"Problem working on {curr_path}")

            if str(file.split('.')[-1]).lower() in ['webm']:
                os.replace(curr_path, os.path.join(WEBM_PATH, file))
                print(f'WEBM: {curr_path}')
                continue
            

if __name__ == '__main__':
    main()