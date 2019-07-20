import datetime
import time
from threading import Thread, Semaphore
from setting import *
from spyderpro.function.peoplefunction.posititioningscence import ScenceFlow
from spyderpro.function.peoplefunction.positioningtrend import PositioningTrend
from spyderpro.function.peoplefunction.positioningsituation import PositioningSituation
from spyderpro.function.peoplefunction.monitoring_area import PositioningPeople

db = pymysql.connect(host=host, user=user, password=password, database=database,
                     port=port)

cur = db.cursor()


class ManagerScence(ScenceFlow, PositioningTrend, PositioningSituation, PositioningPeople):

    def manager_scence_situation(self):
        """
        景区客流数据管理----半小时一轮

        """
        wait = Semaphore(10)
        sql = "select pid from digitalsmart.scencemanager where flag=1"
        try:
            cur.execute(sql)
            db.commit()
        except Exception as e:
            print(e)
            db.rollback()
            return
        pids = cur.fetchall()

        for pid in pids:
            region_id = pid[0]

            def fast(reg_pid):
                db2 = pymysql.connect(host=host, user=user, password=password, database=database,
                                      port=port)  # 必须重新connect，不然由于高并发导致数据库混乱报错
                instances = self.get_scence_situation(db=db2, peoplepid=reg_pid)
                wait.release()
                for info in instances:
                    sql = "insert into digitalsmart.scenceflow(pid, ddate, ttime, num) values ('%d','%d','%s','%d')" % (
                        info.region_id, info.date, info.detailTime, info.num)
                    self.write_data(db, sql)

            wait.acquire()
            Thread(target=fast, args=(region_id,)).start()

        db.close()

    def manager_scence_trend(self):
        """
        地区人口趋势数据管理
        :return:
        """
        d = self.get_place_index(name='深圳欢乐谷', placeid=6, date_start='2019-07-18', date_end='2019-07-19')

    def manager_scenece_people(self):
        sql = "select pid from digitalsmart.scencemanager where flag=0"
        try:
            cur.execute(sql)
            db.commit()
        except Exception as e:
            print(e)
            db.rollback()
            return
        pids = cur.fetchall()
        wait = Semaphore(20)
        d = datetime.datetime.today()
        ddate = str(d.date())
        tmp_date = d.timestamp()  # 更新时间
        if d.time().minute % 5 > 0:
            t = d.time()
            minute = t.minute - t.minute % 5
            detailtime = "{0:0>2}:{1:0>2}:00".format(t.hour, minute)
        else:
            detailtime = time.strftime("%H:%M:00", time.localtime(tmp_date))

        for pid in pids:
            wait.acquire()
            region_id = pid[0]
            data = self.get_data(date=ddate, dateTime=detailtime, region_id=region_id)
            db2 = pymysql.connect(host=host, user=user, password=password, database=database,
                                  port=port)  # 因为这个非常慢
            Thread(target=self.manager_scenece_people_distribution, args=(data, region_id, tmp_date)).start()
            Thread(target=self.manager_scenece_people_situation(data, region_id, ddate, detailtime)).start()
            print("do")
            wait.release()

    def manager_scenece_people_distribution(self, data,region_id, tmp_date: int):
        """
        地区人口分布数据管理
        :return:
        """
        db2 = pymysql.connect(host=host, user=user, password=password, database=database,
                              port=port)  # 因为这个非常慢
        instances = self.get_distribution_situation(data)

        for item in instances:
            sql = "insert into digitalsmart.peopleposition0(pid, tmp_date, lat, lon, num) VALUES" \
                  " ('%d','%d','%f','%f','%d')" % (region_id, tmp_date, item.latitude, item.longitude, item.number)
            self.write_data(db2, sql)

    def manager_scenece_people_situation(self, data, pid, date, ttime):
        """
        地区人口情况数据管理
        :return:

        """
        db2 = pymysql.connect(host=host, user=user, password=password, database=database,
                              port=port)  # 因为这个非常慢
        # time.strftime("%YYYY-%mm-%dd %HH:%MM:00",time.localtime())

        instance = self.get_count(data, date, ttime, pid)
        sql = "insert into digitalsmart.scenceflow(pid, ddate, ttime, num) values ('%d','%d','%s','%d')" % (
            instance.region_id, instance.date, instance.detailTime, instance.num)
        self.write_data(db2, sql)

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
