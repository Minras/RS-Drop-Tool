import csv
import json
import os
import random
import re
import shutil
import sqlite3
import time

import requests


def save_json(input):
    with open('itemlist.json', 'w') as outfile:
        json.dump(input, outfile)

def create_db_structure(conn):
    c = conn.cursor()
    drop_sql = 'DROP TABLE IF EXISTS item'
    c.execute(drop_sql)

    create_sql = '''
CREATE TABLE item (
  id integer PRIMARY KEY AUTOINCREMENT,
  name string,
  normal_name string,
  image string,
  members boolean,
  tradable boolean,
  equipable boolean,
  stackable boolean,
  weight float,
  quest boolean,
  examine string,
  high_alch integer,
  low_alch integer
);
    '''
    c.execute(create_sql)
    create_sql = '''
CREATE TABLE monster (
	id integer PRIMARY KEY AUTOINCREMENT,
	name string,
	normal_name string,
	combat_level integer,
	hp integer,
	max_hit integer,
	race string,
	members boolean,
	quest boolean,
	nature string,
	attack_style string,
	examine string,
	locations string,
	tactic string,
	notes string,
	drops string,
	top_drops string
);
    '''
    c.execute(create_sql)
    create_sql = '''
CREATE TABLE loot (
	id integer PRIMARY KEY AUTOINCREMENT,
	item_id integer,
	monster_id integer,
	rarity_id integer
);
    '''
    c.execute(create_sql)
    create_sql = '''
CREATE TABLE loot_rarity (
	id integer PRIMARY KEY AUTOINCREMENT,
	name string
);
    '''
    c.execute(create_sql)
    create_index_sql = "CREATE INDEX item_normal_name_idx ON item(normal_name);"
    c.execute(create_index_sql)
    create_index_sql = "CREATE INDEX monster_normal_name_idx ON monster(normal_name);"
    c.execute(create_index_sql)
    conn.commit()


def save_db(data, conn):
    print "started saving initial data to db"
    c = conn.cursor()
    c.execute("DELETE FROM item")

    insert_sql = "INSERT INTO item (id, name, normal_name) VALUES (?, ?, ?)"
    ctr = 0
    batch_size = 200
    for key, value in data.iteritems():
        ctr += 1
        params = (key, value, normalize_name(value))
        c.execute(insert_sql, params)
        if 0 == ctr % batch_size:
            print "saved {} records of initial data".format(batch_size)
            conn.commit()
    conn.commit()
    print "finished saving initial data to db"

def normalize_name(name):
    return re.sub('\s+', '_', name.lower())

def urlify_normal_name(name):
    return re.sub('_', '+', name.lower())

def parse_item_list():
    print "started parsing the text data"
    output = {}
    with open('itemlist.txt') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t')
        for row in csv_reader:
            if row[1].lower() != 'null':
                output[str(row[0])] = row[1]
    print "finished parsing the text data"
    print 'processed {line_count} lines.'.format(line_count=len(output))
    return output

@DeprecationWarning
def fetch_zybez(conn):
    print "started crawling zybez"
    c = conn.cursor()
    for row in c.execute('SELECT DISTINCT normal_name FROM item'):
        url = 'http://forums.zybez.net/runescape-2007-prices/api/item/' + urlify_normal_name(row[0])
        # contents = urllib2.urlopen(url).read()
        print url

def crawl_sublimism():
    c = 0
    url_tpl = 'http://www.sublimism.com/misc/idb/img/{}.png'
    path_tpl = 'img/{}.png'
    not404 = True
    error_treshold = 10
    #http://www.sublimism.com/misc/idb/img/1.png
    while not404:
        c += 1
        local_file = path_tpl.format(c)
        if os.path.exists(local_file):
            print "{} already exists. skipping.".format(local_file)
            break

        time.sleep(random.uniform(1.0, 1.2))
        # contents = urllib2.urlopen(tpl.format(c)).read()
        r = requests.get(url_tpl.format(c), stream=True)
        if r.status_code == 200:
            with open(local_file, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
            print "{} created.".format(local_file)
        else:
            error_treshold -= 1
            print "#{} file error".format(c)
            if 0 == error_treshold:
                not404 = False



data = parse_item_list()

# crawl_sublimism()

conn = sqlite3.connect('rsparser.db')
create_db_structure(conn)
save_db(data, conn)
#fetch_zybez(conn)
conn.close()