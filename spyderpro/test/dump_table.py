import csv
import os
import pymysql

user = 'root'
password = 'lzs87724158'
host = "localhost"
port = 3306
scencefilepath = os.getcwd()
city_file_path = os.getcwd()
database = 'digitalsmart'
db = pymysql.connect(host=host, user=user, password=password, database=database,
                     port=port)

cur = db.cursor()
sql = "select pid,tmp_date,area,rate,name,flag from digitalsmart.searchrate"
cur.execute(sql)
f= open("/Users/darkmoon/Project/SpyderPr/datafile/searchrate.csv",'a+')
w = csv.writer(f)
for item in cur.fetchall():
    w.writerow(item)
    f.flush()
