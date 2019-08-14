import sys
import os
import requests
import datetime
from threading import Thread, Semaphore
from spyderpro.function.trafficfunction.traffic import Traffic
from setting import *
from pymysql.connections import Connection

db: Connection = pymysql.connect(host=host, user=user, password=password,
                                 database=database,
                                 port=port)
cur = db.cursor()


class ManagerTraffic(Traffic):
    def __init__(self):
        self.taskSemaphore = Semaphore(5)  # 任务并发锁头🔒
        self.pidLock = Semaphore(1)  # 数据锁🔒

    def manager_city_traffic(self):
        """
        获取城市实时交通拥堵情况并写入数据库,半小时执行一次
        :return:
        """

        sql = "select pid from digitalsmart.citymanager"
        cur.execute(sql)
        data = cur.fetchall()  # 获取pid集合
        for item in data:
            self.taskSemaphore.acquire()
            self.pidLock.acquire()
            pid = item[0]

            def fast(region_id):
                db2: Connection = pymysql.connect(host=host, user=user, password=password,
                                                  database=database,
                                                  port=port)
                info = self.get_city_traffic(citycode=region_id, db=db2)  # 获取交通数据
                if len(info) == 0:
                    print("%d没有数据" % (region_id))
                    self.taskSemaphore.release()

                    return
                # 数据写入
                for item in info:
                    sql = "insert into  digitalsmart.citytraffic(pid, ddate, ttime, rate)" \
                          " values('%d', '%d', '%s', '%f');" % (
                              region_id, item.date, item.detailtime, item.index)
                    self.write_data(db2, sql)
                self.taskSemaphore.release()
                db2.close()

            # fast(pid)
            Thread(target=fast, args=(pid,)).start()
            self.pidLock.release()

    def manager_city_road_traffic(self):
        """
        获取每个城市实时前10名拥堵道路数据-----10分钟执行一遍
        :return:
        """
        up_date = datetime.datetime.now().timestamp()  # 记录最新的更新时间

        sql = "select pid from digitalsmart.citymanager"
        cur.execute(sql)
        data = cur.fetchall()  # pid集合
        for item in data:  # 这里最好不要并发进行，因为每个pid任务下都有10个子线程，在这里开并发 的话容易被封杀

            pid = item[0]

            def fast(region_id):

                db2: Connection = pymysql.connect(host=host, user=user, password=password,
                                                  database=database,
                                                  port=port)
                resultObjs = self.road_manager(region_id)  # 获取道路数据

                for obj in resultObjs:
                    region_id = obj.region_id
                    roadname = obj.roadname
                    speed = obj.speed
                    direction = obj.direction
                    bounds = obj.bounds
                    indexSet = obj.data
                    rate = obj.rate
                    roadid = obj.num  # 用排名表示道路id
                    sql = "insert into digitalsmart.roadtraffic(pid, roadname, up_date, speed, direction, bound, data," \
                          "roadid,rate) VALUE" \
                          "(%d,'%s',%d,%f,'%s','%s','%s',%d,%f) " % (
                              region_id, roadname, up_date, speed, direction, bounds,
                              indexSet, roadid,rate)
                    self.write_data(db2, sql)
                    sql = "update  digitalsmart.roadmanager set up_date={0}  where pid={1} and roadid={2}" \
                        .format(up_date, region_id,roadid)
                    self.write_data(db2, sql)  # 更新最近更新时间

                db2.close()

            fast(pid)
            # Thread(target=fast, args=(pid,)).start()
            # self.pidLock.release()

    def manager_city_year_traffic(self):

        sql = "select yearpid from digitalsmart.citymanager"
        cur.execute(sql)
        data = cur.fetchall()
        for item in data:
            self.taskSemaphore.acquire()
            self.pidLock.acquire()
            yearpid = item[0]

            def fast(region_id):
                print(region_id)
                db2: Connection = pymysql.connect(host=host, user=user, password=password,
                                                  database=database,
                                                  port=port)
                resultObj = self.yeartraffic(region_id, db2)
                for item in resultObj:
                    region_id = item.region_id
                    date = item.date
                    index = item.index
                    sql = "insert into digitalsmart.yeartraffic(pid, tmp_date, rate) VALUE (%d,%d,%f)" % (
                        region_id, date, index)
                    self.write_data(db, sql)
                self.taskSemaphore.release()
                db2.close()

            Thread(target=fast, args=(yearpid,)).start()
            # fast(yearpid)

            self.pidLock.release()

    def clear_road_data(self):
        """
        清除昨天的道路数据
        :return:
        """
        sql = "truncate table digitalsmart.roadtraffic"
        try:
            cur.execute(sql)
            db.commit()
        except Exception:
            db.rollback()


# ManagerTraffic().manager_city_road_traffic()
