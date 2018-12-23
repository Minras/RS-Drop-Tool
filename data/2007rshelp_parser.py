import os
import random
import re
import shutil
import time

import requests
from bs4 import BeautifulSoup

url_tpl = 'https://2007rshelp.com/monsters.php?order=ASC&category=combat&page={page}&search_area=combat&search_term={search_term}'
pages = {'1-25': 12,
         '26-50': 7,
         '51-80': 6,
         '81-781': 10}
dir_monster_ranges = 'monster_ranges'
dir_monsters = 'monsters'
pattern_monsters_url = ur'/monsters.php\?id=(\d+)'


def dump_url(url, filename):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(filename, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
        print "{} created.".format(filename)
    else:
        print "#{} file error".format(filename)
        return False
    return True

def dump_monster_ranges():
    error_counter = 0
    path_tpl = 'monster_ranges/r{range}-p{page}.html'
    for search_term, max_page in pages.iteritems():
        for page in range(1, max_page+1):
            url = url_tpl.format(page=page, search_term=search_term)
            local_file = path_tpl.format(range=search_term, page=page)
            if os.path.exists(local_file):
                print "{} already exists. skipping.".format(local_file)
                continue
            time.sleep(random.uniform(1.0, 1.2))
            if not dump_url(url, local_file):
                error_counter += 1
    print "finished saving monster ranges. error count: {}".format(error_counter)

def parse_monster_ranges():
    for filename in os.listdir(dir_monster_ranges):
        filename_path = os.path.join(dir_monster_ranges, filename)
        if not os.path.isfile(filename_path):
            continue
        with open(filename_path) as fp:
            soup = BeautifulSoup(fp, "html.parser")
            #monsterstable
            table = soup.find(id="monsterstable")
            for a in table.find_all('a'):
                if re.match(pattern_monsters_url, a.get('href')):
                    yield a.get('href')


def dump_monsters():
    path_tpl = 'monsters/{id}.html'
    url_tpl = 'https://2007rshelp.com{}'
    for a in parse_monster_ranges():
        id = re.match(pattern_monsters_url, a).group(1)
        url = url_tpl.format(a)
        filename = path_tpl.format(id=id)
        if os.path.exists(filename):
            print "{} already exists. skipping.".format(filename)
            continue
        time.sleep(random.uniform(0.3, 0.6))
        if not dump_url(url, filename):
            print "error saving file {}".format(filename)
        else:
            print "OK {}".format(filename)
        # print "OK {}".format(filename)

# dump_monster_ranges()
dump_monsters()
