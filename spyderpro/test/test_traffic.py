import csv
import os
from spyderpro.models.traffic.gaodetraffic import GaodeTraffic


def get_new_year_traffic_data():
    gao = GaodeTraffic()
    writepath = os.path.abspath(os.path.join(os.path.pardir, "../datafile/城市季度交通情况2/"))
    filepath = os.path.abspath(os.path.join(os.path.pardir, "../datafile/gaodecity.csv"))
    f = open(filepath, 'r')
    read = csv.reader(f)
    for item in read:
        pid = int(item[0])
        city = item[1]
        wf = open(''.join([writepath, '/', city, '.csv']), 'a+')
        w = csv.writer(wf)
        for i in range(1, 4):
            year_iter = gao.yeartraffic(pid, 2019, i)
            for obj in year_iter:
                ddate = obj.date
                rate = obj.index
                w.writerow([ddate, rate])

        wf.close()


if __name__ == "__main__":
    get_new_year_traffic_data()