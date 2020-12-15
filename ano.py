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
import sqlite3

def get_config():
    with open('config.yml') as f:
        return yaml.load(f, Loader=yaml.FullLoader)

class Row:
    def __init__(self, *args, **kwargs):
        if len(args) == 9:
            self.user_id = args[0]
            self.date = datetime(int(args[1]), int(args[2]), int(args[3]), int(args[4]), int(args[5]), int(args[6]))
            self.lattitude = args[7]
            self.longitude = args[8]

    def __str__(self):
        return('\t'.join([self.user_id, str(self.date), str(self.lattitude), str(self.longitude)]))

class Database:
    def __init__(self, config):
        self.config = config
        self.conn = sqlite3.connect('svp.db')
        self.c = self.conn.cursor()

        self.c.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name='svp';''')
        if self.c.fetchone() == None:
            self.c.execute('''CREATE TABLE svp (user_id, year, month, day, hour, min, second, lattitude, longitude)''')
            self.fill()

    def fill(self):
        fin = open(self.config['original_file'], "r")
        reader = csv.reader(fin)
        original = list(reader)
        fin.close()

        for data in original:
            row = Row()
            row_data = data[0].split("\t")
            row.user_id = row_data[0]

            year, month, day = list(map(int,row_data[1][0:10].split("-")))
            hour, min, sec = list(map(int,row_data[1][11:19].split(":")))
            row.date = datetime(year, month, day, hour, min, sec)

            row.lattitude = float(row_data[2])
            row.longitude = float(row_data[3])
            self.c.execute("INSERT INTO svp VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (row.user_id, row.date.year, row.date.month, row.date.day, row.date.hour, row.date.minute, row.date.second, row.lattitude, row.longitude))
        self.conn.commit()

    def print(self):
        for row in self.c.execute('SELECT * FROM svp'):
            print(row)

    def write(self):
        fout = open(self.config['ano_file'],"w")
        for row in self.c.execute('SELECT * FROM svp'):
            output_row = Row(*row)
            writer = output_row.__str__() + '\n'
            fout.write(writer)
        fout.close()

    def close(self):
        self.conn.close()

    def get_number_of_rows(self):
        self.c.execute('SELECT COUNT(*) from svp')
        return self.c.fetchone()[0]

    def run_query(self, query):
        return self.c.execute(query)

def swap_coordinates(row1, row2):
    row1.lattitude, row2.lattitude = row2.lattitude, row1.lattitude
    row1.longitude, row2.longitude = row2.longitude, row1.longitude

def add_gaussian_noise(row, sigma):
    row.lattitude += random.gauss(0, sigma)
    row.longitude += random.gauss(0, sigma)

def run_utility_metrics(config):
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

def main():
    config = get_config()
    db = Database(config)
    #db.print()
    #db.write()
    for row in db.run_query('SELECT * FROM svp'):
        print(row)
        
    run_utility_metrics(config)

if __name__ == "__main__":
    main()
