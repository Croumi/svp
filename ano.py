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

class User:
    def __init__(self, user_id):
        self.user_id = user_id
        self.dictOfLong = {}
        self.dictOfLatt = {}
        self.dictOfPOI = {}
        self.occur = 0
        self.coef_suppresion_row = random.randint(1,5)
        
    def __str__(self):
        return('\t'.join([str(self.user_id), str(self.dictOfPOI), str(self.occur)]))

    def addElement(self, row, mode, cellsize = 2 ):
        long = str(round(row.longitude, cellsize))
        lat = str(round(row.lattitude, cellsize))
        couple = long +" "+ lat
        if (couple in self.dictOfPOI and mode == 1):
            if (self.dictOfPOI[couple] < (self.occur/self.coef_suppresion_row)):
                self.dictOfPOI[couple] += 1
            else :
                row.user_id = "DEL"
        else :
            self.dictOfPOI[couple] = 1

        if (long in self.dictOfLong and lat in self.dictOfLatt and mode == 0):
            if (self.dictOfLong[long] < (self.occur/self.coef_suppresion_row) and self.dictOfLatt[lat] < (self.occur/self.coef_suppresion_row)):
                self.dictOfLong[long] += 1
                self.dictOfLatt[lat] += 1
            else :
                row.user_id = "DEL"
        else :
            self.dictOfLong[long] = 1
            self.dictOfLatt[lat] = 1
        self.occur += 1

class Row:
    def __init__(self, row_data):
        self.user_id = row_data[0]
        year, month, day = list(map(int,row_data[1][0:10].split("-")))
        hour, min, sec = list(map(int,row_data[1][11:19].split(":")))
        self.date = datetime(year, month, day, hour, min, sec)
        self.lattitude = float(row_data[2])
        self.longitude = float(row_data[3])
        self.treshold = 0.99

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
        if random.random() > self.treshold:
            new_hour = (self.date.hour + (random.randint(-1, 1)))%24
            if self.date.hour > night_start or self.date.hour < night_end or (self.date.hour > work_start and self.date.hour < work_end):
                if abs(self.date.hour - new_hour) <= 1:
                    self.date = self.date.replace(hour = new_hour)

    def add_random_noise_to_min_sec(self):
        if random.random() > self.treshold:
            #self.date = self.date.replace(minute = random.randint(0, 59), second = random.randint(0, 59))
            self.date = self.date + timedelta(minutes = self.date.minute + random.randint(-1, 1), seconds = self.date.second + random.randint(-10, 10))

    def adapt_hour(self):
        if self.date.weekday() < 5:
            if 22 <= self.date.hour < 24:
                if random.random() > self.treshold:
                    self.date = self.date.replace(hour = 23)
            elif 0 <= self.date.hour < 2:
                if random.random() > self.treshold:
                    self.date = self.date.replace(hour = 1)
            elif 3 <= self.date.hour < 6:
                if random.random() > self.treshold:
                    self.date = self.date.replace(hour = 5)
            elif 6 <= self.date.hour < 9:
                self.date = self.date.replace(hour = 7)
            elif 9 <= self.date.hour < 12:
                if random.random() > self.treshold:
                    self.date = self.date.replace(hour = 10)
            elif 12 <= self.date.hour < 14:
                if random.random() > self.treshold:
                    self.date = self.date.replace(hour = 13)
            elif 14 <= self.date.hour < 16:
                if random.random() > self.treshold:
                    self.date = self.date.replace(hour = 15)
            elif 16 <= self.date.hour < 19:
                self.date = self.date.replace(hour = 17)
            elif 19 <= self.date.hour < 22:
                self.date = self.date.replace(hour = 20)
        else :
            if  0 <= self.date.hour < 4:
                self.date = self.date.replace(hour = 1)
            elif  4 <= self.date.hour < 7:
                self.date = self.date.replace(hour = 5)
            elif  7 <= self.date.hour < 10:
                self.date = self.date.replace(hour = 8)
            elif 10 <= self.date.hour < 14:
                if random.random() > self.treshold:
                    self.date = self.date.replace(hour = 12)
            elif 14 <= self.date.hour < 18:
                if random.random() > self.treshold:
                    self.date = self.date.replace(hour = 16)
            elif 18 <= self.date.hour < 21:
                self.date = self.date.replace(hour = 19)
            elif 21 <= self.date.hour < 24:
                self.date = self.date.replace(hour = 22)

    def change_date(self):
        if random.random() > self.treshold:
            if (self.date.weekday() == 0):
                self.date = self.date + timedelta(days = 1)
            elif (self.date.weekday() == 2):
                self.date = self.date + timedelta(days = -1)
            elif (self.date.weekday() == 3):
                self.date = self.date + timedelta(days = 1)
            elif (self.date.weekday() == 5):
                self.date = self.date + timedelta(days = 1)

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

def isolate_user(row, tabOfUser, tabOfUserId):
    tabOfUser[(tabOfUserId.index(row.user_id))].addElement(row,1)

def main():
    config, original, fout = init()
    tabOfUserId = []
    tabOfUser = []
    for (index, data) in enumerate(original):
        row_data = data[0].split("\t")
        row = Row(row_data)
        if row.user_id not in tabOfUserId:
            # print(row.user_id, " a été rajouté")
            user = User(row.user_id)
            tabOfUserId.append(str(row.user_id))
            tabOfUser.append(user)
        isolate_user(row, tabOfUser, tabOfUserId)
        row.add_random_noise_within_cell()
        row.adapt_hour()
        row.add_random_noise_to_hour()
        row.add_random_noise_to_min_sec()
        row.change_date()
        row.write(config, fout)
    print("Finished writing to file")
    end(config, fout)

if __name__ == "__main__":
    main()
