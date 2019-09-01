# Create your tests here.
import csv
import time
import random
import os
import pymysql
import json
import shutil
import requests
from threading import Thread
from selenium import webdriver

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


def send_scence_pic():
    db = pymysql.connect(host='localhost', user="root", password="lzs87724158",
                         database="digitalsmart", port=3306)
    cur = db.cursor()
    sql = "select area,pid from digitalsmart.scencemanager where flag=0 "
    cur.execute(sql)
    result = cur.fetchall()
    rootpath = "/Volumes/Tigo/易班项目数据/景区评论及图片/景区/"

    area_map = dict()
    for item in result:
        area = item[0]
        pid = item[1]
        area_map[area] = pid
    count = 0
    for filedir in os.listdir(rootpath):

        key = get_pid(area_map, filedir)
        if key is not None:
            pid = area_map[key]

            for file in os.listdir(rootpath + filedir):
                file_type = file.split(".")[1]
                count += 1
                if file_type == "png" or file_type == "jpg" or file_type == "jpeg":
                    filepath = rootpath + filedir + "/" + file
                    newfilename = str(int(time.time()) + count) + '.' + file_type
                    newfile = "/Users/darkmoon/Project/DigitalSmart/digitalsmart/media/photo/" + newfilename
                    shutil.copy(filepath, newfile)
                    sql = "insert into digitalsmart.photodb(pid, photo) VALUE(%d,'%s')" % (pid, "photo/" + newfilename)

                    cur.execute(sql)
    db.commit()


def get_pid(map, longkey):
    for key in map.keys():
        if key in longkey:
            return key
    else:
        return None


if __name__ == "__main__":  # send:吉安市井冈山风景名胜区
    # send_scence_pic()
    # Thread(target=send_scence_pic, args=()).start()
    # send_comment_data()
    sql = "select pid,photo from digitalsmart.photodb"
    cur.execute(sql)
    db.close()
    user = 'root'
    password = 'lzs87724158'
    host = "39.108.13.150"
    port = 3306
    scencefilepath = os.getcwd()
    city_file_path = os.getcwd()
    database = 'digitalsmart'
    db = pymysql.connect(host=host, user=user, password=password, database=database,
                         port=port)

    server_cur = db.cursor()
    for item in cur.fetchall():
        pid =item[0]
        photo =item[1]
        sql = "insert into digitalsmart.photodb(pid, photo) VALUE (%d,'%s')"%(pid, photo)
        server_cur.execute(sql)
        print(sql)
    db.commit()