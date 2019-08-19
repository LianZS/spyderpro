import csv
import sys
import os

sys.path[0] = os.path.abspath(os.path.curdir)
from setting import *

rootpath = os.path.abspath(os.path.pardir)

db = pymysql.connect(host=host, user=user, password=password, database=database,
                     port=port)
cur = db.cursor()


def initUserHabit():
    sql = "select id from digitalsmart.userhabit"
    cur.execute(sql)
    if len(cur.fetchall()) >= 10:
        print("整体用户应用安装行为userhabit数据库已经初始化了")
        return
    filepath = os.path.join(rootpath, 'datafile/normalInfo/整体用户行为.csv')
    f = open(filepath)
    r = csv.reader(f)
    r.__next__()
    for item in r:  # 日期,人均安装应用,人均启动应用
        ddate = item[0]
        aver_install = int(item[1])
        aver_start = int(item[2])
        sql = "insert into digitalsmart.userhabit(ddate, installnum, activenum) value ('%s',%d,%d)" % (
            ddate, aver_install, aver_start)
        try:
            cur.execute(sql)
            db.commit()
        except Exception as e:
            print(e)
            db.rollback()
    f.close()


def initAppInfo():
    """
    初始化app对照表
    """
    sql = "select id from digitalsmart.appinfo"
    cur.execute(sql)
    if len(cur.fetchall()) >= 1000:
        print("APP对照表appinfo数据库已经初始化了")
        return
    filepath = os.path.join(rootpath, 'datafile/normalInfo/appinfo.csv')
    f = open(filepath)
    r = csv.reader(f)
    r.__next__()
    for item in r:  # （标识,app）
        pid = int(item[0])
        app = item[1]
        sql = "insert into digitalsmart.appinfo(id, name) VALUE (%d,'%s')" % (pid, app)
        try:
            cur.execute(sql)
            db.commit()
        except Exception as e:
            print(e, pid, app)
            db.rollback()
    f.close()


def initAppActive():
    """
    初始化app活跃数据
    :return:
    """
    sql = "select id from digitalsmart.appactive"
    cur.execute(sql)
    if len(cur.fetchall()) >= 3000:
        print("app活跃信息表appactive已经初始化了")
        return

    filepath = os.path.join(rootpath, 'datafile/normalInfo/appactive.csv')
    f = open(filepath)
    r = csv.reader(f)
    r.__next__()
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

        try:
            cur.execute(sql)
            db.commit()
        except Exception as e:
            print(e, pid, app)
            db.rollback()
    f.close()


# def initAgeShare():
#     #还未完成，还有appactive.csv有问题
#     """初始化app年龄分布"""
#
#     filepath = os.path.join(rootpath, 'datafile/normalInfo/appbaseinfo.csv')
#     f = open(filepath)
#     r = csv.reader(f)
#     r.__next__()
#     for item in r:  # (app,日期,省份热度[{}],年龄分布[{}],性别分布[{}],内容关键词热度[{}])
#
#         app = item[0]
#         ddate = item[1]
#         provincerate = item[2]  # 可能为空
#         ageshare = item[3]  # 可能为空
#         sexshare = item[4]  # 可能为空
#         keywordrate = item[5]  # 可能为空
#         if provincerate == ""
#             provincerate = []
#         if ageshare == "":
#             ageshare = []
#         if sexshare == "":
#             sexshare = []
#
#         if keywordrate == "":
#             keywordrate = []




if __name__ == "__main__":
    initUserHabit()
    initAppInfo()
    initAppActive()
    # initAgeShare()
    cur.close()
    db.close()
