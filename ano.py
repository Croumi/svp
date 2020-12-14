import csv
import random
from datetime import datetime
import yaml

def get_config():
    with open('config.yml') as f:
        return yaml.load(f, Loader=yaml.FullLoader)

class Row:
    def __init__(self):
        pass

    def __str__(self):
        return('\t'.join([row.user_id, str(row.date), row.lattitude, row.longitude]))

def swap_coordinates(row1, row2):
    row1.lattitude, row2.lattitude = row2.lattitude, row1.lattitude
    row1.longitude, row2.longitude = row2.longitude, row1.longitude

def add_gaussian_noise(row, sigma):
    row.lattitude += random.gauss(0, sigma)

if __name__ == "__main__":
    config = get_config()
    fin = open(config['original_file'],"r")
    fout = open(config['ano_file'],"w")
    reader = csv.reader(fin)
    original = list(reader)
    rows = []
    for data in original:
        row = Row()
        row_data = data[0].split("\t")
        row.user_id = row_data[0]

        year, month, day = list(map(int,row_data[1][0:10].split("-")))
        hour, min, sec = list(map(int,row_data[1][11:19].split(":")))
        row.date = datetime(year, month, day, hour, min, sec)

        row.lattitude = row_data[2]
        row.longitude = row_data[3]
        rows.append(row)

    for row in rows:
        writer = '\t'.join([row.user_id, str(row.date), row.lattitude, row.longitude]) + '\n'
        fout.write(writer)

    fin.close()
    fout.close()
