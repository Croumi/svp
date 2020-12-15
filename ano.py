import csv
import random
from datetime import datetime
import yaml
import sys
sys.path.append('metrics')
import yaml
import dateUtil
import hourUtil
import utility_distance
import utility_meet
import utility_POI
import utility_POI_perWeek
import utility_tuile

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

def write_rows(config, rows):
    fout = open(config['ano_file'],"w")
    for row in rows:
        writer = row.__str__() + '\n'
        fout.write(writer)
    fout.close()

def main():
    config = get_config()
    rows = get_rows(config)
    edit_rows(rows)
    write_rows(config, rows)

    original_file = config['original_file']
    ano_file = config['ano_file']
    utility_metrics = [
        dateUtil,
        hourUtil,
        utility_distance,
        utility_meet,
        utility_POI,
        utility_POI_perWeek,
        utility_tuile
    ]
    for metric in utility_metrics:
        print(metric.__name__ + " : " + str(getattr(metric, "main")(original_file, ano_file)))

if __name__ == "__main__":
    main()
