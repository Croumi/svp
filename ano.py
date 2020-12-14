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
        return('\t'.join([self.user_id, str(self.date), str(self.lattitude), str(self.longitude)]))

def swap_coordinates(row1, row2):
    row1.lattitude, row2.lattitude = row2.lattitude, row1.lattitude
    row1.longitude, row2.longitude = row2.longitude, row1.longitude

def add_gaussian_noise(row, sigma):
    row.lattitude += random.gauss(0, sigma)

def get_rows(config):
    fin = open(config['original_file'],"r")
    reader = csv.reader(fin)
    original = list(reader)
    fin.close()

    rows = []
    for data in original:
        row = Row()
        row_data = data[0].split("\t")
        row.user_id = row_data[0]

        year, month, day = list(map(int,row_data[1][0:10].split("-")))
        hour, min, sec = list(map(int,row_data[1][11:19].split(":")))
        row.date = datetime(year, month, day, hour, min, sec)

        row.lattitude = float(row_data[2])
        row.longitude = float(row_data[3])
        rows.append(row)
    return rows

def edit_rows(rows):
    for row in rows:
        add_gaussian_noise(row, 0.01)

def write_rows(config):
    fout = open(config['ano_file'],"w")
    for row in rows:
        writer = row.__str__() + '\n'
        fout.write(writer)
    fout.close()

if __name__ == "__main__":
    config = get_config()
    rows = get_rows(config)
    edit_rows(rows)
    write_rows(config)
