import pymysql
import os
import csv
from threading import Thread, Semaphore

user = 'root'
password = 'lzs87724158'
host = "47.103.105.236"
port = 3306
database = 'digitalsmart'
rootpath = os.path.abspath(os.path.join(os.path.curdir))
dirpath = rootpath + "/Traffic/"
try:
    os.mkdir(dirpath)
except Exception:
    pass
db = pymysql.connect(host=host, user=user, password=password, database=database,
                     port=port)
cur = db.cursor()
sql = "select pid,name from digitalsmart.citymanager "
cur.execute(sql)
lock = Semaphore(10)
for pid, name in cur.fetchall():
    print(pid, name)


    def fast(filename, region_id):
        f = open(dirpath + filename + ".csv", "a+")
        w = csv.writer(f)
        newdb = pymysql.connect(host=host, user=user, password=password, database=database,
                                port=port)
        newcur = newdb.cursor()
        sql = 'select  ddate,ttime,rate  from digitalsmart.citytraffic where pid={0}'.format(region_id)
        newcur.execute(sql)

        for ddate, ttime, rate in newcur.fetchall():
            w.writerow([ddate, ttime, rate])
        f.close()
        newdb.close()
        lock.release()


    lock.acquire()
    Thread(target=fast, args=(name, pid,)).start()
