import time
import os
import sys
import requests
import json
import urllib.request
import bs4
from PIL import Image, UnidentifiedImageError
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from Post import Post
from Thread import Thread

OUTPUT_PATH = os.path.join(os.path.expanduser('~'), 'Downloads')
OUTPUT_DIR = r'/image-dump'
MANIFEST_NAME = 'manifest.tsv'
ALL_BOARDS = ['b','c','d','e','f','g','gif','h','hr','k','m','o','p','r','s',
    't','u','v','vg','vm','vmg','vr','vrpg','vst','w','wg','i','ic','r9k',
    's4s','vip','qa','cm','hm','lgbt','y','3','aco','adv','an','bant','biz',
    'cgl','ck','co','diy','fa','fit','gd','hc','his','int','jp','lit','mlp',
    'mu','n','news','out','po','pol','pw','qst','sci','soc','sp','tg','toy',
    'trv','tv','vp','vt','wsg','wsr','x','xs']

def main():
    # py main.py (thread_url)

    load_dotenv()
    if len(sys.argv) > 1 and sys.argv[1].startswith('https://boards.4chan.org/'):
        url = sys.argv[1]
        (board, id) = get_board_thread_from_url(url)
        print(f"Attempting to explore board {board} thread #{id}")
        extract_images_from_thread(url)
        return
    
    # py main.py
    board = input("What board to copy? /").lower().replace('/','')    
    if not board in ALL_BOARDS:
        print(f"Not a valid board: '{board}'")
        return
    catalog_url = f'https://boards.4chan.org/{board}/catalog'
    print(f"Success! Scanning {catalog_url}")
    catalog_response = requests.get(catalog_url)
    if not is_ok(catalog_response):
        return
    
    catalog_soup = BeautifulSoup(catalog_response.text, 'html.parser')
    threads = parse_catalog_for_thread_list(catalog_soup)
    
    mode = input("What to do? (1=select thread(s) from list | 2=all threads)")
    match mode:
        case '1':
            i = 0
            print(f'There are {len(threads)} threads.')
            for i, t in enumerate(threads):
                print(f'{i}.\t{t}')            

            input_strings = input('Which threads? (Separated by spaces): ').split(' ')
            for ind in input_strings:
                index_int = int(ind)
                thread_id = threads[index_int].id
                url = f'https://boards.4chan.org/{board}/thread/{thread_id}'
                extract_images_from_thread(url)
        case '2':
            print("Downloading all threads. This will take a while...")
            i = 0
            for i, thread in enumerate(threads):
                id = thread.id
                url = f'https://boards.4chan.org/{board}/thread/{id}'
                print(f'{i}/{len(threads)}, {url}')
                extract_images_from_thread(url)


def get_board_thread_from_url(url: str):
    if not url.startswith('https://boards.4chan.org/'):
        print("Bad url must be something like 'https://boards.4chan.org/wg/thread/7977599'")
        return None
    parts = url.split('/thread/')
    board = parts[0].split('/')[-1]
    thread_id = int(parts[1].split('/')[0])
    return (board, thread_id)
        

def extract_images_from_thread(url: str) -> None:
    (board, id) = get_board_thread_from_url(url)
    thread_response = requests.get(url)
    if not is_ok(thread_response):
        return
    
    # now assume status 200
    html = thread_response.text
    soup = BeautifulSoup(html, 'html.parser')
    posts: dict[int, Post] = {}
    containers: list[bs4.element.Tag] = soup.find_all('div', class_='postContainer')
    for c in containers:
        # get post url if any
        url = None
        if c.find('a', class_='fileThumb'):
            url = c.find('a', class_='fileThumb').attrs.get('href', url)

        # get post id
        post_id = c.find('span', class_='postNum').find_all('a')[-1].text

        # get post UTC timestamp
        timestamp = c.find('span', class_='dateTime').attrs['data-utc']

        # get the post's text, if there is any
        post_text = c.find('blockquote').get_text(separator='<__newline__>', strip=True)
        post = Post(url, int(post_id), int(timestamp), post_text)
        posts[post_id] = post

    # check that the full path exists
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)

    # build the dir path and write the manifest of images and comments for this thread
    path = build_dir_path(board, id)
    file_path = fr'{path}/{MANIFEST_NAME}'
    if not os.path.isfile(file_path):
        with open(file_path, 'a+') as f:
            f.write('id\ttimestamp\timage\turl\tsuccess\ttext\n')

    # remove potential repeat items
    count = 0
    with open(file_path, "r") as file:
        for line in file:
            items = line.split('\t')
            if items[0] == 'id':
                continue
            print(f'EXISTING: {items[0]}')
            posts.pop(items[0], None)
            count = count + 1
    print(f"There are {count} items on the list. {len(posts.items())} will be reviewed for addition.")        

    # add new items to the manifest and files
    manifest_file = open(file_path, 'a')
    i = 0
    for i, p in enumerate(posts.values()):
        if p.image_url == '':
            continue
        
        # Avoid HTTP error 429
        time.sleep(5)
        image_name = f'{p.image_url.split("/")[-1]}'
        this_path = fr'{path}/{image_name}'
        print(f"{i+1}. Downloading {image_name} from {p.image_url}")
        was_successful = 1
        try:
            this_path = fr'{path}/{image_name}'
            urllib.request.urlretrieve(p.image_url, this_path)
            if not image_name.endswith("webm") and not image_name.endswith("mp4") and not image_name.endswith(".gif"):
                Image.open(this_path)
        except UnidentifiedImageError as e:
            print(f"\tCorrupt Image. Deleting {image_name}")
            os.remove(this_path)
            was_successful = 0
        except Exception as e:
            print(f"\tDownload Failed for {p.image_url} -> {image_name}: {e}")
            was_successful = 0
        finally:
            if was_successful == 1:
                manifest_file.write(f'{p.post_id}\t{p.post_timestamp}\t{p.image_url}\t{was_successful}\t{p.post_content}\n')


def is_ok(response: requests.Response):
    if str(response.status_code).startswith('4'):
        print(f"Error getting response. Bad URL? {response.status_code}")
        return False
    elif str(response.status_code).startswith('5'):
        print(f"Something is wrong with the server. Cannot continue. {response.status_code}")
        return False
    return True


def parse_catalog_for_thread_list(soup: bs4.BeautifulSoup) -> list[Thread]:
    scripts: bs4.element.Tag = soup.find_all('script')
    found_script = ''
    for script in scripts:
        temp = script.get_text()
        if temp.find('var catalog = {') > -1:
            found_script = temp
            break
    if found_script == '':
        print("count not find thread json")
        return
    
    final_json = None
    try:
        catalog_json = found_script.split(';var catalog = ')[-1].split(';var style_group = ')[0]
        final_json = json.loads(catalog_json)
    except:
        return []
    
    all_threads = []
    for th in final_json['threads']:
        try:
            thread_id = th
            thread_title = final_json['threads'][th]['sub']
            thread_desc = final_json['threads'][th]['teaser']
            thread_responses = final_json['threads'][th]['r']
            thread_num_images = final_json['threads'][th]['i']
            this_thread = Thread(int(thread_id), thread_title, thread_desc, thread_responses, thread_num_images)
            all_threads.append(this_thread)
        except:
            print("Failed to parse a json object")
    return all_threads


def build_dir_path(board: str, thread: str | int):
    if not os.path.exists(fr'{OUTPUT_PATH}{OUTPUT_DIR}'):
        os.makedirs(fr'{OUTPUT_PATH}{OUTPUT_DIR}')
    if not os.path.exists(fr'{OUTPUT_PATH}{OUTPUT_DIR}/{board}'):
        os.makedirs(fr'{OUTPUT_PATH}{OUTPUT_DIR}/{board}')
    if not os.path.exists(fr'{OUTPUT_PATH}{OUTPUT_DIR}/{board}/{thread}'):
        os.makedirs(fr'{OUTPUT_PATH}{OUTPUT_DIR}/{board}/{thread}')
    return fr'{OUTPUT_PATH}{OUTPUT_DIR}/{board}/{thread}'

if __name__ == '__main__':
    main()