import os
import random
import shutil
import time

import requests

url_tpl = 'https://2007rshelp.com/monsters.php?order=ASC&category=combat&page={page}&search_area=combat&search_term={search_term}'
pages = {'1-25': 12,
         '26-50': 7,
         '51-80': 6,
         '81-781': 10}


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
            r = requests.get(url, stream=True)
            if r.status_code == 200:
                with open(local_file, 'wb') as f:
                    r.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)
                print "{} created.".format(local_file)
            else:
                error_counter += 1
                print "#{} file error".format(local_file)
    print "finished saving monster ranges. error count: {}".format(error_counter)


dump_monster_ranges()
