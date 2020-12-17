import csv
import random
from datetime import datetime
from datetime import timedelta
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
import os
import multiprocessing

class Row:
    def __init__(self, row_data):
        self.user_id = row_data[0]
        year, month, day = list(map(int,row_data[1][0:10].split("-")))
        hour, min, sec = list(map(int,row_data[1][11:19].split(":")))
        self.date = datetime(year, month, day, hour, min, sec)
        self.lattitude = float(row_data[2])
        self.longitude = float(row_data[3])

    def __str__(self):
        return('\t'.join([self.user_id, str(self.date), str(self.lattitude), str(self.longitude)]))

    def write(self, config, fout):
        writer = self.__str__() + '\n'
        fout.write(writer)

    def add_gaussian_noise(self, sigma):
        self.lattitude += random.gauss(0, sigma)
        self.longitude += random.gauss(0, sigma)

    def add_random_noise_within_cell(self, cellsize = 2):
        precision = 1
        for _ in range(cellsize):
            precision /= 10

        self.lattitude = round(self.lattitude, cellsize) + 1.00005 * precision * (random.random() - 0.5)
        self.longitude = round(self.longitude, cellsize) + 1.00005 * precision * (random.random() - 0.5)

    #def add_random_noise_to_date(self):
    #    if random.random() > 0.85:
    #        self.date += timedelta(days = 1) * (random.randint(-1, 1))

    def add_random_noise_to_hour(self):
        night_start, night_end = 22, 6
        work_start, work_end = 9, 16
        if random.random() > 0.97:
            new_hour = (self.date.hour + (random.randint(-1, 1)))%24
            if self.date.hour > night_start or self.date.hour < night_end or (self.date.hour > work_start and self.date.hour < work_end):
                self.date = self.date.replace(hour = new_hour)

    def add_random_noise_to_min_sec(self):
        self.date = self.date.replace(minute = random.randint(0, 59), second = random.randint(0, 59))
        
    #def swap_coordinates(row):
    #    self.lattitude, row.lattitude = row.lattitude, self.lattitude
    #    self.longitude, row.longitude = row.longitude, self.longitude
    #    return row

def get_config():
    with open('config.yml') as f:
        return yaml.load(f, Loader=yaml.FullLoader)

def init():
    config = get_config()
    if os.path.exists(config['ano_file']):
      os.remove(config['ano_file'])
    fin = open(config['original_file'],"r")
    original = list(csv.reader(fin))
    fin.close()
    fout = open(config['ano_file'],"a")
    return config, original, fout

def end(config, fout):
    fout.close()
    run_utility_metrics(config)

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

    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    jobs = []
    for i in range(len(utility_metrics)):
        p = multiprocessing.Process(target= utility_metrics[i].main, args=(original_file, ano_file, return_dict))
        jobs.append(p)
        p.start()

    for proc in jobs:
        proc.join()

    for metric in return_dict.keys():
        print("{} : {}".format(metric, return_dict[metric]))

    values = list(map(float, return_dict.values()))
    average = sum(values) / len(values)
    print("average : {}".format(average))

def main():
    config, original, fout = init()

    for (index, data) in enumerate(original):
        row_data = data[0].split("\t")
        row = Row(row_data)
        row.add_random_noise_within_cell()
        row.add_random_noise_to_hour()
        row.add_random_noise_to_min_sec()
        row.write(config, fout)
        print("wrote row number {} : ({})".format(index, row))

    end(config, fout)

if __name__ == "__main__":
    main()
