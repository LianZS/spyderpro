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
rootpath = os.path.abspath(os.path.curdir)

filepath = os.path.join(rootpath, '')
f = open(filepath + "searchrate.csv")
r = csv.reader(f)
count = 0
for item in r:  # 6,20160101,深圳欢乐谷,0,wechat,0
    pid = int(item[0])
    ddate = int(item[1])
    area = item[2]
    num = int(item[3])
    name = item[4]
    flag = int(item[5])
    sql = "insert into digitalsmart.searchrate(pid, tmp_date, area, rate, name, flag) " \
          "VALUE (%d,%d,'%s',%d,'%s',%d)" % (pid, ddate, area, num, name, flag)
    cur.execute(sql)
    count += 1
    if count % 1111 == 0:
        db.commit()
db.commit()
