import csv
import os
import pymysql
from threading import  Thread
user = 'root'
password = 'lzs87724158'
host = "localhost"
port = 3306
scencefilepath = os.getcwd()
city_file_path = os.getcwd()
database = 'digitalsmart'


def upload_app_active_data():
    """
    初始化app活跃数据
    :return:
    """
    db = pymysql.connect(host=host, user=user, password=password, database=database,
                         port=port)

    cur = db.cursor()

    rootpath = os.path.abspath(os.path.curdir)

    sql = "select id from digitalsmart.appactive"
    cur.execute(sql)
    if len(cur.fetchall()) >= 3000:
        print("app活跃信息表appactive已经初始化了")
        return

    filepath = os.path.join(rootpath, '')
    f = open(filepath + "appactive.csv")
    r = csv.reader(f)
    r.__next__()
    count = 0
    for item in r:  # （标识,app名,日期,活跃数,活跃度,行业活跃度基准值,行业活跃度均值）
        try:
            pid = int(item[0])
            app = item[1]
            ddate = item[2]
            activenum = int(item[3])
            activerate = float(item[4])
            base_activerate = float(item[5])
            aver_activerate = float(item[6])
        except Exception:
            continue

        sql = "insert into digitalsmart.appactive(pid, ddate, activenum, activerate, base_activerate, aver_activerate) VALUE(" \
              "%d,'%s',%d,%f,%f,%f) " % (pid, ddate, activenum, activerate, base_activerate, aver_activerate)
        cur.execute(sql)
        count += 1
        if count % 1001 == 0:
            db.commit()

    db.commit()
    f.close()


def upload_app_like():
    # 上传app用户偏好数据
    db = pymysql.connect(host=host, user=user, password=password, database=database,
                         port=port)

    cur = db.cursor()
    rootpath = os.path.abspath(os.path.curdir)

    sql = "select id,name from digitalsmart.appinfo"

    cur.execute(sql)
    app_map = dict()
    for item in cur.fetchall():
        pid = item[0]
        app = item[1]
        app_map[app] = pid
    filepath = os.path.join(rootpath, '')
    f = open(filepath + "appbaseinfo.csv")
    r = csv.reader(f)  # app,日期,省份热度,年龄分布,性别分布,内容关键词热度
    r.__next__()
    count = 0
    for item in r:  # (app,日期,省份热度[{}],年龄分布[{}],性别分布[{}],内容关键词热度[{}])

        app = item[0]
        pid = app_map[app]
        ddate = item[1]

        # provincerate = item[2]  # 可能为空
        # ageshare = item[3]  # 可能为空
        # sexshare = item[4]  # 可能为空
        keywordrate = item[5]  # 可能为空
        # if provincerate == "":
        #     provincerate = []
        # if ageshare == "":
        #     ageshare = []
        # if sexshare == "":
        #     sexshare = []

        if keywordrate == "":
            continue
        key_rate_list = eval(keywordrate)
        for key_map in key_rate_list:
            key_name = key_map['name']
            key_rate = float(key_map['share'])
            sql = "insert into digitalsmart.applike(pid, ddate, keyword, rate) VALUE (%d,'%s','%s',%f)" % (
                pid, ddate, key_name, key_rate)
            cur.execute(sql)
            count += 1
            if count % 1111 == 0:
                print("commit")
                db.commit()

    db.commit()


def upload_app_age_share():
    # 上传app用户年龄比例数据
    db = pymysql.connect(host=host, user=user, password=password, database=database,
                         port=port)

    cur = db.cursor()
    rootpath = os.path.abspath(os.path.curdir)

    sql = "select id,name from digitalsmart.appinfo"

    cur.execute(sql)
    app_map = dict()
    for item in cur.fetchall():
        pid = item[0]
        app = item[1]
        app_map[app] = pid
    filepath = os.path.join(rootpath, '')
    f = open(filepath +  "appbaseinfo.csv")
    r = csv.reader(f)  # app,日期,省份热度,年龄分布,性别分布,内容关键词热度
    r.__next__()
    count = 0
    for item in r:  # (app,日期,省份热度[{}],年龄分布[{}],性别分布[{}],内容关键词热度[{}])

        app = item[0]
        pid = app_map[app]
        ddate = item[1]

        ageshare = item[3]  # 可能为空

        if ageshare == "":
            continue

        age_share_list = eval(ageshare)
        under_nineth = nin_twen = twe_thir = thir_four = four_fift = over_fift = None
        for key_map in age_share_list:
            key_name = key_map['name']
            if key_name == "19岁以下":
                under_nineth = float(key_map['share'])
            if key_name == "19-25岁":
                nin_twen = float(key_map['share'])
            if key_name == "26-35岁":
                twe_thir = float(key_map['share'])
            if key_name == "36-45岁":
                thir_four = float(key_map['share'])
            if key_name == "46-55岁":
                four_fift = float(key_map['share'])
            if key_name == "55岁以上":
                over_fift = float(key_map['share'])
        if not (under_nineth and nin_twen and twe_thir and thir_four and four_fift and over_fift):
            if under_nineth is None:
                under_nineth = 0
            if nin_twen is None:
                nin_twen = 0
            if twe_thir is None:
                twe_thir = 0
            if thir_four is None:
                thir_four = 0
            if four_fift is None:
                four_fift = 0
            if over_fift is None:
                over_fift = 0

        sql = "insert into digitalsmart.ageshare(pid, ddate, under_nineth, nin_twen, twe_thir, thir_four, four_fift, over_fift) " \
              "VALUE (%d,'%s',%f,%f,%f,%f,%f,%f)" % (
                  pid, ddate, under_nineth, nin_twen, twe_thir, thir_four, four_fift, over_fift)
        cur.execute(sql)
        count += 1
        if count % 1111 == 0:
            print("commit")
            db.commit()

    db.commit()
def upload_app_province_share():
    # 上传app省份热度数据
    db = pymysql.connect(host=host, user=user, password=password, database=database,
                         port=port)

    cur = db.cursor()
    rootpath = os.path.abspath(os.path.curdir)

    sql = "select id,name from digitalsmart.appinfo"

    cur.execute(sql)
    app_map = dict()
    for item in cur.fetchall():
        pid = item[0]
        app = item[1]
        app_map[app] = pid
    filepath = os.path.join(rootpath, '')
    f = open(filepath +  "appbaseinfo.csv")
    r = csv.reader(f)  # app,日期,省份热度,年龄分布,性别分布,内容关键词热度
    r.__next__()
    count = 0
    for item in r:  # (app,日期,省份热度[{}],年龄分布[{}],性别分布[{}],内容关键词热度[{}])

        app = item[0]
        pid = app_map[app]
        ddate = item[1]

        provincerate = item[2]  # 可能为空

        if provincerate == "":
             continue

        key_rate_list = eval(provincerate)
        for key_map in key_rate_list:
            key_name = key_map['name']
            key_rate = float(key_map['share'])
            sql = "insert into digitalsmart.app_province_share(pid, ddate, province, rate) VALUE (%d,'%s','%s',%f)" % (
                pid, ddate, key_name, key_rate)
            cur.execute(sql)
            count += 1
            if count % 1111 == 0:
                print("commit")
                db.commit()

    db.commit()


Thread(target=upload_app_province_share,args=()).start()
Thread(target=upload_app_age_share,args=()).start()
Thread(target=upload_app_like,args=()).start()