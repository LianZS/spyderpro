import time
from typing import Iterator, List
from pymysql.connections import Connection

from spyderpro.models.traffic.baidutraffic import BaiduTraffic
from spyderpro.models.traffic.gaodetraffic import GaodeTraffic
from setting import *
from concurrent.futures import ThreadPoolExecutor
from spyderpro.portconnect.sqlconnect import MysqlOperation
from spyderpro.instances.trafficclass import TrafficClass, Year


class Traffic(MysqlOperation):
    instance = None

    @classmethod
    def dailycitytraffic(cls, citycodelist: list):
        while True:
            if cls.instance is None:
                cls.instance = super().__new__(cls)
            cls.instance.programmerpool(cls.instance.get_city_traffic, citycodelist)

    def get_city_traffic(self, citycode: int, db: Connection) -> List[TrafficClass]:
        """
        获取城市实时交通拥堵指数数据
        :param citycode:
        :return:List[TrafficClass]
        """

        traffic = None
        if citycode > 1000:
            traffic = GaodeTraffic()

        elif 0 < citycode < 1000:

            traffic = BaiduTraffic()
        else:
            return []
        t = time.time()  # 现在的时间
        # 分好昨今以便分类过滤
        today = int(time.strftime('%Y%m%d', time.localtime(t)))
        yesterday = int(time.strftime('%Y%m%d', time.localtime(t - 3600 * 24)))

        info = traffic.citytraffic(citycode)
        if not info:  # 请求失败
            return []
        info = self.__dealwith_daily_traffic(info, citycode, db, today, yesterday)  # 过滤掉昨天和已经存在的数据

        return info

    def __dealwith_daily_traffic(self, info, pid, db, today, yesterday) -> List[TrafficClass]:
        """
        重复数据处理
        :param info: 数据包
        :param pid: 城市id
        :param db: 数据库实例
        :param today: 今天日期
        :param yesterday: 昨天日期
        :return: list
        """
        # 将昨天的数据全部剔除

        objs = list(info)
        for i in range(len(objs)):

            if objs[i].date > yesterday:
                objs = objs[i:]
                break
        "下面是过滤今天已经存在的数据---今天重复的数据剔除"
        sql = "select ttime from  digitalsmart.citytraffic where pid={0} and ddate={1} order by ttime".format(pid,
                                                                                                              today)
        cursor = self.get_cursor(db, sql)
        if cursor == "error":  # cursor()失败
            return []


        else:
            data = cursor.fetchall()
            if len(data):
                ttime = str(data[len(data) - 1][0]) if len(str(data[len(data) - 1][0])) == 8 else "0" + str(
                    data[len(data) - 1][0])  # 最新的时间  xx:xx:xx
            else:
                ttime = "-1:00:00"  # 今天还未录入数据的情况
        cursor.close()
        # 剔除今天重复的数据
        info = self.filter(objs, ttime)

        return info

    def road_manager(self, citycode):
        """
        获取城市道路拥堵数据并写入数据库
        :param citycode: 城市id
        :return: bool
        """
        g = None
        if citycode > 1000:
            g = GaodeTraffic()
        elif citycode < 1000:
            g = BaiduTraffic()
        result = g.roaddata(citycode)
        if result is None:
            return []

        return result

    def yeartraffic(self, yearpid: int, db: Connection):

        g = None
        if yearpid > 1000:
            g = GaodeTraffic()
        elif yearpid < 1000:
            g = BaiduTraffic()

        result = g.yeartraffic(yearpid)
        result = self.__dealwith_year_traffic(result, yearpid, db,
                                              lastdate=int(time.strftime("%Y%m%d",
                                                                         time.localtime(time.time() - 24 * 3600))))
        return result

    def __dealwith_year_traffic(self, info: Iterator, pid: int, db: Connection, lastdate: int) -> List[Year]:
        sql = "select tmp_date from digitalsmart.yeartraffic where pid={0} and tmp_date>= {1} order by tmp_date".format(
            pid, lastdate)
        cursor = self.get_cursor(db, sql)
        if cursor == "error":
            print("年度数据查询日期数据失败！")
            return []
        data = cursor.fetchall()
        if not data:
            return list(info)
        result:int = data[-1]  # 最近的日期
        info = list(info)
        i = -1
        for i in range(len(info)):
            if info[i].date == result:
                break
        return info[i + 1:]

    @staticmethod
    def programmerpool(func, pidlist):
        """
        并发，不建议使用
        :param func:
        :param pidlist:
        :return:
        """
        tasklist = []

        threadpool = ThreadPoolExecutor(max_workers=6)

        for Pid in pidlist:
            task = threadpool.submit(func, Pid)
            tasklist.append(task)
        while [item.done() for item in tasklist].count(False):
            pass

    # 数据过滤器
    @staticmethod
    def filter(info: list, detailtime: str) -> List[TrafficClass]:
        """
        过滤数据，清空已存在的数据
        :param info:数据包
        :param date:日期
        :param detailtime:具体时间段
        :return:list
        """
        for i in range(len(info)):

            if info[i].detailtime == detailtime:
                info = info[i + 1:]
                break
        return info

    def find_name(self, citycode: int, db) -> str:
        """
        查询城市名字
        :param citycode:  城市id
        :param db: 数据库实例
        :return: str ->城市名
        """
        sql = "select  name from trafficdatabase.MainTrafficInfo where cityCode=" + str(citycode) + ";"
        cursor = db.cursor()
        cityname = None
        try:
            cursor.execute(sql)
            db.commit()
            cityname = cursor.fetchone()[0]

        except TypeError as e:
            print("数据库执行出错:%s" % e)
            db.rollback()
            cursor.close()
        return cityname
