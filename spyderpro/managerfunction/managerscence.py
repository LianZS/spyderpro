import datetime
import time
from threading import Thread, Semaphore
from queue import Queue
from setting import *
from spyderpro.function.peoplefunction.posititioningscence import ScenceFlow
from spyderpro.function.peoplefunction.positioningtrend import PositioningTrend
from spyderpro.function.peoplefunction.positioningsituation import PositioningSituation
from spyderpro.function.peoplefunction.monitoring_area import PositioningPeople

db = pymysql.connect(host=host, user=user, password=password, database=database,
                     port=port)

cur = db.cursor()


class ManagerScence(ScenceFlow, PositioningTrend, PositioningSituation, PositioningPeople):
    def __init__(self):
        self.connectqueue = Queue(10)  # 最多十个数据库连接
        for i in range(10):
            self.connectqueue.put(pymysql.connect(host=host, user=user, password=password, database=database,
                                                  port=port))

        self.wait = Semaphore(10)  # 单个任务中最多开10个线程同时进行

    def manager_scence_situation(self):
        """
        景区客流数据管理----半小时一轮

        """
        lock = Semaphore(1)
        taskwait = Semaphore(10)
        sql = "select pid from digitalsmart.scencemanager where flag=1"
        try:
            cur.execute(sql)
            db.commit()
        except Exception as e:
            print(e)
            db.rollback()

        pids = cur.fetchall()

        for pid in pids:

            def fast(reg_pid):
                db2 = pymysql.connect(host=host, user=user, password=password, database=database,
                                      port=port)  # 必须重新connect，不然由于高并发导致数据库混乱报错
                instances = self.get_scence_situation(db=db2, peoplepid=reg_pid)
                taskwait.release()
                for info in instances:
                    sql = "insert into digitalsmart.scenceflow(pid, ddate, ttime, num) values ('%d','%d','%s','%d')" % (
                        info.region_id, info.date, info.detailTime, info.num)
                    self.write_data(db, sql)
                db2.close()

            taskwait.acquire()
            lock.acquire()
            region_id = pid[0]
            Thread(target=fast, args=(region_id,)).start()
            lock.release()

        db.close()

    def manager_scence_trend(self):
        """
        地区人口趋势数据管理
        :return:
        """
        d = self.get_place_index(name='深圳欢乐谷', placeid=6, date_start='2019-07-18', date_end='2019-07-19')

    def manager_scenece_people(self):
        sql = "select pid,latitude,longitude from digitalsmart.scencemanager where flag=0"
        try:
            cur.execute(sql)
            db.commit()
        except Exception as e:
            print(e)
            db.rollback()
            return
        data = cur.fetchall()
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
            self.wait.acquire()
            lock.acquire()
            region_id = item[0]
            lat = item[1]
            lon = item[2]

            def fast(cid):
                data = self.get_data(date=ddate, dateTime=detailtime, region_id=cid)
                if not data:
                    return
                Thread(target=self.manager_scenece_people_distribution,
                       args=(data, region_id, tmp_date, lat, lon)).start()
                Thread(target=self.manager_scenece_people_situation(data, region_id, ddate, detailtime)).start()
                print("do")

            Thread(target=fast, args=(region_id,)).start()
            lock.release()

    def manager_scenece_people_distribution(self, data, region_id, tmp_date: int, centerlat: float, centerlon: float):
        """
        地区人口分布数据---这部分每次只有几k条数据插入
        :return:
        """
        db2 = self.connectqueue.get()
        newcur = db2.cursor()
        instances = self.get_distribution_situation(data)
        count = 0  # 每一百条提交一次
        for item in instances:
            sql = "insert into digitalsmart.peopleposition0(pid, tmp_date, lat, lon, num) VALUES" \
                  " ('%d','%d','%f','%f','%d')" % (
                      region_id, tmp_date, centerlat + item.latitude, centerlon + item.longitude, item.number)
            try:
                newcur.execute(sql)
            except Exception as e:
                print(e)
                continue
            count += 1
            if count == 100:
                db2.commit()
        newcur.close()
        self.wait.release()
        db2.commit()
        print("success")
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


ManagerScence().manager_scenece_people()
