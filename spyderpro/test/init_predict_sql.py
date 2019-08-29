import csv
import os
import re
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
sql = "select pid,area from digitalsmart.scencemanager"
cur.execute(sql)
area_map = dict()
for pid, area in cur.fetchall():
    area_map[area] = pid
f = open("/Volumes/Tigo/易班项目数据/非节假日模型.csv")
r = csv.reader(f)
r.__next__()
for area, model in r:
    pid = area_map[area]
    powers, formula = model.split("\n")
    powers = powers.strip(" ")
    try:
        hpower, spower = re.findall("(\d)", powers)
    except Exception as e:
        print(area, powers, e)
        continue
    hpower = int(hpower)
    spower = int(spower)
    lpower = 1
    polynomial = formula.split("x")
    hconstant = eval(polynomial[0])
    sconstant = eval(polynomial[1])
    lconstant = eval(polynomial[2])
    mconstant = eval(polynomial[3])
    sql = "insert into digitalsmart.predictmodel(hpower, spower, lpower,lconstant, hconstant, sconstant, pid, mconstant) " \
          "VALUE (%d,%d,%d,%f,%f,%f,%d,%f)" % (hpower, spower, lpower, lconstant, hconstant, sconstant, pid, mconstant)
    cur.execute(sql)
    db.commit()
f = open("/Volumes/Tigo/易班项目数据/节假日模型.csv")
r = csv.reader(f)
r.__next__()
for area, model in r:
    pid = area_map[area]
    powers, formula = model.split("\n")
    powers = powers.strip(" ")
    try:
        hpower, spower = re.findall("(\d)", powers)
    except Exception as e:
        print(area, powers, e)
        continue
    hpower = int(hpower)
    spower = int(spower)
    lpower = 1
    polynomial = formula.split("x")
    hconstant = eval(polynomial[0])
    sconstant = eval(polynomial[1])
    lconstant = eval(polynomial[2])
    mconstant = eval(polynomial[3])
    sql = "insert into digitalsmart.predictmodel(hpower, spower, lpower,lconstant, hconstant, sconstant, pid, mconstant,flag) " \
          "VALUE (%d,%d,%d,%f,%f,%f,%d,%f,%d)" % (hpower, spower, lpower, lconstant, hconstant, sconstant, pid, mconstant,1)
    cur.execute(sql)
    db.commit()