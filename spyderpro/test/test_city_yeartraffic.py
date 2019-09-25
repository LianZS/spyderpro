import csv
import os
import pymysql
from spyderpro.data_requests.traffic.baidutraffic import BaiduTraffic

user = 'root'
password = 'lzs87724158'
host = "39.108.13.150"
port = 3306
scencefilepath = os.getcwd()
city_file_path = os.getcwd()
database = 'digitalsmart'
db = pymysql.connect(host=host, user=user, password=password, database=database,
                     port=port)
cur = db.cursor()
sql = "select pid,yearpid from digitalsmart.citymanager where pid=yearpid and pid<10000"
cur.execute(sql)
baidu = BaiduTraffic()
for item in cur.fetchall():
    yearid = item[0]
    result = baidu.yeartraffic(yearid, 2019, 1)
    for colum in result:
        sql = "insert into digitalsmart.yeartraffic(pid, tmp_date, rate) VALUE (%d,%d,%f)" % (
        colum.region_id, colum.date, colum.index)
        print(sql)
        cur.execute(sql)
    print("commit")
    db.commit()
