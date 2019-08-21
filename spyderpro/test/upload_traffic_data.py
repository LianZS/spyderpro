import csv
import os
import pymysql

user = 'root'
password = 'lzs87724158'
host = "47.103.105.236"
port = 3306
scencefilepath = os.getcwd()
city_file_path = os.getcwd()
database = 'digitalsmart'


def upload_data_to_server():
    # 上传app活跃度数据上服务器数据库
    readpath = os.path.abspath(os.path.join(os.path.pardir, "../datafile/城市季度交通情况/"))

    db = pymysql.connect(host=host, user=user, password=password, database=database,
                         port=port)

    cur = db.cursor()
    sql = "select pid,name,yearpid from digitalsmart.citymanager"
    cur.execute(sql)
    result = cur.fetchall()
    for pid, city, yearpid in result:
        try:
            f = open(''.join([readpath, '/', city, '.csv']), 'r')
        except FileNotFoundError:
            continue
        read = csv.reader(f)
        read.__next__()
        print(city)
        for item in read:
            ddate = int(item[0].replace("-", ""))
            rate = float(item[1])
            sql = "insert into digitalsmart.yeartraffic(pid, tmp_date, rate) VALUE (%d,%d,%f)" % (yearpid, ddate, rate)
            print(sql)
            cur.execute(sql)
        db.commit()
    db.close()
    print("success")





if __name__ == "__main__":
    upload_data_to_server()
