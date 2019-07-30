import sys
import os

import datetime
import time
from threading import Thread, Semaphore
from queue import Queue
from setting import *
from spyderpro.function.peoplefunction.posititioningscence import ScenceFlow
from spyderpro.function.peoplefunction.positioningtrend import PositioningTrend
from spyderpro.function.peoplefunction.positioningsituation import PositioningSituation
from spyderpro.function.peoplefunction.monitoring_area import PositioningPeople

global_db = Semaphore(1)
db = pymysql.connect(host=host, user=user, password=password, database=database,
                     port=port)

cur = db.cursor()


class ManagerScence(ScenceFlow, PositioningTrend, PositioningSituation, PositioningPeople):

    def __init__(self):
        self.connectqueue = Queue(15)  # 最多十个数据库连接
        for i in range(15):
            self.connectqueue.put(pymysql.connect(host=host, user=user, password=password, database=database,
                                                  port=port))

        self.taskSemaphore = Semaphore(10)  # 单个任务中最多开10个线程同时进行

    def manager_scence_situation(self):
        """
        景区客流数据管理----半小时一轮

        """
        lock = Semaphore(1)
        wait = Semaphore(10)
        sql = "select pid from digitalsmart.scencemanager where flag=1"
        global_db.acquire()
        try:
            cur.execute(sql)
            db.commit()
        except Exception as e:
            print(e)
            db.rollback()

        pids = cur.fetchall()
        global_db.release()
        for pid in pids:

            def fast(reg_pid):
                db2 = pymysql.connect(host=host, user=user, password=password, database=database,
                                      port=port)  # 必须重新connect，不然由于高并发导致数据库混乱报错
                instances = self.get_scence_situation(db=db2, peoplepid=reg_pid)
                wait.release()
                for info in instances:
                    sql = "insert into digitalsmart.scenceflow(pid, ddate, ttime, num) values ('%d','%d','%s','%d')" % (
                        info.region_id, info.date, info.detailTime, info.num)
                    self.write_data(db2, sql)

                db2.close()

            wait.acquire()
            lock.acquire()
            region_id = pid[0]
            Thread(target=fast, args=(region_id,)).start()
            lock.release()

        print("success")

    def manager_scence_trend(self):
        """
        地区人口趋势数据管理---5分钟一次
        :return:
        """
        today = datetime.datetime.today()
        t = datetime.timedelta(days=1)
        tomorrow = today + t
        start = str(today.date())
        end = str(tomorrow.date())
        sql = "select pid,area from digitalsmart.scencemanager where flag=0 "
        global_db.acquire()
        cur.execute(sql)
        data = cur.fetchall()
        global_db.release()
        lock = Semaphore(1)
        wait = Semaphore(10)  # 之所以不用实例属性的信号量，是因为他们任务是同时进行的
        for item in data:
            wait.acquire()
            lock.acquire()
            pid = item[0]
            area = item[1]

            def fast(region_id, place):
                db2 = self.connectqueue.get()
                sql = "select ttime from digitalsmart.scencetrend where pid={0} and ddate='{1}' order by ttime".format(
                    region_id, int(start.replace("-", "")))
                cur2 = db2.cursor()
                cur2.execute(sql)
                last_ttime = "-1:00:00"
                try:
                    last_ttime = str(cur2.fetchall()[-1][0])
                except IndexError as e:
                    print(e)

                resultObjs = self.get_place_index(name=place, placeid=region_id, date_start=start, date_end=end)
                c = 0
                for obj in resultObjs:
                    ttime = obj.detailtime
                    if ttime <= last_ttime:
                        continue

                    region_id = obj.region_id
                    ddate = obj.ddate
                    rate = obj.index
                    sql = "insert into digitalsmart.scencetrend(pid, ddate, ttime, rate) VALUE(%d,%d,'%s',%f)" % (
                        region_id, ddate, ttime, rate)
                    if self.write_data(db2, sql):
                        print("insert success")
                    c += 1
                self.connectqueue.put(db2)

            wait.release()
            Thread(target=fast, args=(pid, area)).start()
            lock.release()

    def manager_scenece_people(self):
        up_date = int(datetime.datetime.now().timestamp())
        global_db.acquire()
        sql = "select pid,latitude,longitude from digitalsmart.scencemanager where flag=0"
        try:
            cur.execute(sql)
            db.commit()
        except Exception as e:
            print(e)
            db.rollback()
            return
        data = cur.fetchall()
        global_db.release()
        lock = Semaphore(1)

        d = datetime.datetime.today()
        ddate = str(d.date())
        tmp_date = d.timestamp()  # 更新时间
        if d.time().minute % 5 > 0:
            t = d.time()
            minute = t.minute - t.minute % 5
            detailtime = "{0:0>2}:{1:0>2}:00".format(t.hour, minute)
        else:
            detailtime = time.strftime("%H:%M:00", time.localtime(tmp_date))

        for item in data:

            self.taskSemaphore.acquire()
            lock.acquire()
            region_id = item[0]

            lat = item[1]
            lon = item[2]
            db2 = self.connectqueue.get()
            newcur = db2.cursor()
            sql = "select table_id from digitalsmart.tablemanager where pid={0}".format(region_id)
            newcur.execute(sql)

            table_id = newcur.fetchone()[0]  # 数据对应在哪张表插入
            self.connectqueue.put(db2)

            def fast(cid, tale_pid):
                data = self.get_data(date=ddate, dateTime=detailtime, region_id=cid)
                if not data:
                    return
                Thread(target=self.manager_scenece_people_distribution,
                       args=(data, cid, up_date, lat, lon, tale_pid)).start()
                Thread(target=self.manager_scenece_people_situation(data, cid, ddate, detailtime)).start()

            Thread(target=fast, args=(region_id, table_id)).start()
            lock.release()

    def manager_scenece_people_distribution(self, data, region_id, tmp_date: int, centerlat: float, centerlon: float,
                                            table_id: int):
        """
        地区人口分布数据---这部分每次有几k条数据插入
        :return:
        """
        instances = self.get_distribution_situation(data)

        db2 = self.connectqueue.get()
        newcur = db2.cursor()
        count = 0  # 每一百条提交一次
        table = "digitalsmart.peopleposition{0}".format(table_id)  # 确定哪张表
        select_table = "insert into {0}(pid, tmp_date, lat, lon, num) VALUES" \
                       " ('%d','%d','%f','%f','%d')".format(table)
        c = 0
        for item in instances:
            sql = select_table % (
                region_id, tmp_date, centerlat + item.latitude, centerlon + item.longitude, item.number)
            try:
                newcur.execute(sql)
            except Exception as e:
                print(e)
                continue
            count += 1
            if count == 100:
                count = 0
                db2.commit()
            c += 1
        print(c)
        self.taskSemaphore.release()
        db2.commit()
        print("success")
        sql = "update digitalsmart.tablemanager  " \
              "set last_date={0} where pid={1}".format(tmp_date, region_id)  # 更新修改时间
        newcur.execute(sql)
        newcur.close()
        db2.commit()
        self.connectqueue.put(db2)

    def manager_scenece_people_situation(self, data, pid, date, ttime):
        """
        地区人口情况数据  ---这部分每次只有一条数据插入
        :return:

        """
        db2 = self.connectqueue.get()
        newcur = db2.cursor()

        # time.strftime("%YYYY-%mm-%dd %HH:%MM:00",time.localtime())
        instance = self.get_count(data, date, ttime, pid)
        sql = "insert into digitalsmart.scenceflow(pid, ddate, ttime, num) values (%d,%d,'%s',%d)" % (
            instance.region_id, instance.date, instance.detailTime, instance.num)
        try:
            newcur.execute(sql)
            newcur.close()
        except Exception as e:
            print(e)
        self.connectqueue.put(db2)

    def manager_china_positioning(self):
        """
        中国人定位数据管理
        :return:
        """
        instances = self.positioning_people_num(max_num=10)

    def manager_monitoring_area(self):
        """"""
        self.get_the_scope_of_pace_data(start_lat=23.2, start_lon=110.2, end_lat=30.2, end_lon=113.2)
