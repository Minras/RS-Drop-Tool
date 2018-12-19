import csv
import json
import sqlite3
import re


def save_json(input):
    with open('itemlist.json', 'w') as outfile:
        json.dump(input, outfile)

def save_db(data):
    conn = sqlite3.connect('rsparser.db')
    c = conn.cursor()
    create_sql = '''
CREATE TABLE IF NOT EXISTS item (
	id integer PRIMARY KEY AUTOINCREMENT,
	name string,
	normal_name string
);
    '''
    c.execute(create_sql)

    c.execute("DELETE FROM item")

    insert_sql = "INSERT INTO item (id, name, name_normal) VALUES (?, ?, ?)"
    ctr = 0
    for key, value in data.iteritems():
        params = (key, value, normalize_name(value))
        c.execute(insert_sql, params)
        if 0 == ctr % 1000:
            conn.commit()

def normalize_name(name):
    return re.sub('\s+', '_', name.lower())

def parse_item_list():
    output = {}
    with open('itemlist.txt') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t')
        for row in csv_reader:
            if row[1].lower() != 'null':
                output[str(row[0])] = row[1]
    print 'Processed {line_count} lines.'.format(line_count=len(output))
    return output


data = parse_item_list()
save_db(data)