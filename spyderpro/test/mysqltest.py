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
sql = "select pid,area from digitalsmart.scencemanager  where flag=0"
cur.execute(sql)
result = cur.fetchall()
path = "/home/FILE/"

for item in result:
    pid = item[0]
    area = item[1]
    filepath = path + area + ".csv"
    try:
        f = open(filepath, 'r')
    except Exception as e:
        # print("[{0},'{1}'],".format(pid,area))
        continue
    print(pid,area)
    read = csv.reader(f)
    count = 0
    for row in read:
        dd = row[0]
        ddate, ttime = dd.split(" ", maxsplit=2)
        ddate = int(ddate.replace("-", ""))
        num = int(row[1])
        sql = "insert into digitalsmart.historyscenceflow (pid, ddate, ttime, num) VALUE (%d,%d,'%s',%d)" % (
        pid, ddate, ttime, num)

        cur.execute(sql)
        count += 1
        if count % 100 == 0:
            db.commit()
    db.commit()
