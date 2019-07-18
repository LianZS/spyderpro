import time
from typing import Iterator, List
from pymysql.connections import Connection

from spyderpro.models.traffic.baidutraffic import BaiduTraffic
from spyderpro.models.traffic.gaodetraffic import GaodeTraffic
from spyderpro.managerfunction.setting import *
from concurrent.futures import ThreadPoolExecutor
from spyderpro.portconnect.sqlconnect import MysqlOperation
from spyderpro.instances.trafficclass import TrafficClass


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
        获取数据
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
        t = time.time()
        today = int(time.strftime('%Y%m%d', time.localtime(t)))
        yesterday = int(time.strftime('%Y%m%d', time.localtime(t - 3600 * 24)))

        info = traffic.citytraffic(citycode)
        info = self.__dealwith_daily_traffic(info, citycode, db, today, yesterday)

        return info

    # 重复数据处理
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
        # 将今天重复的数据剔除
        sql = "select ttime from  digitalsmart.citytraffic where pid={0} and ddate={1} order by ttime".format(pid,
                                                                                                              today)
        cursor = self.get_cursor(db, sql)
        if cursor == "error":
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

    def road_manager(self, citycode) -> bool:
        """
        获取城市道路拥堵数据并写入数据库
        :param citycode: 城市id
        :return: bool
        """
        db = pymysql.connect(host=host, user=user, password=password,
                             database=trafficdatabase,
                             port=port)

        t = time.localtime()
        date = time.strftime("%Y-%m-%d", t)
        detailtime = time.strftime("%H:%M", t)
        g = None
        if citycode > 1000:
            g = gaodetraffic()
        elif citycode < 1000:
            g = baidutraffic()
        result = g.roaddata(citycode)
        if result is None:
            return False
        for item in result:
            sql = "insert into  trafficdatabase.RoadTraffic(pid_id,date,detailTime,name,direction," \
                  "speed,data,bounds,flag) " \
                  "values('%d','%s','%s','%s','%s','%f','%s','%s',%s);" % (
                      citycode, date, detailtime, item['RoadName'], item['Direction'], item['Speed'], item['Data'],
                      item['Bounds'], True)
            if not self.loaddatabase(db, sql):
                print("%s写入数据库失败" % item)
                continue
        print("success")
        db.close()
        return True

    def yeartraffic(self, citycode):
        db = pymysql.connect(host=host, user=user, password=password, database=trafficdatabase,
                             port=port)
        yearpid = self.__search_yearpid(citycode, db)
        g = None
        if yearpid > 1000:
            g = gaodetraffic()
        elif yearpid < 1000:
            g = baidutraffic()
        name = self.find_name(citycode, db)
        result = g.yeartraffic(yearpid, name)
        result = self.__dealwith_year_traffic(result, citycode, db,
                                              lastdate=time.strftime("%Y-%m-%d",
                                                                     time.localtime(time.time() - 24 * 3600)))
        for item in result:
            date = item['date']
            index = item['index']
            city = item['city']
            sql = "insert into  trafficdatabase.YearCityTraffic(pid_id,date,city,TrafficIndex) " \
                  "values('%d','%s','%s','%f')" % (
                      citycode, date, city, index)
            if not self.loaddatabase(db, sql):
                print("%s写入数据库失败" % item)
                continue
        print("success")
        db.close()
        return True

    def __search_yearpid(self, citycode, db):
        sql = "select yearpid from trafficdatabase.MainTrafficInfo WHERE cityCode=" + str(citycode)

        cursor = self.get_cursor(db, sql)
        if cursor is None:
            print("查询失败")
            return None
        try:
            yearpid = cursor.fetchone()[0]
        except TypeError:
            raise TypeError("找不到相关数据")
        if yearpid == 0:
            return citycode
        return yearpid

    def __dealwith_year_traffic(self, info, pid, db, lastdate):
        sql = "select  date  from trafficdatabase.YearCityTraffic where pid_id=" + str(
            pid) + " and date >='" + lastdate + "';"
        cursor = self.get_cursor(db, sql)
        if cursor is None:
            print("年度数据查询日期数据失败！")
            return None
        try:
            result = str(cursor.fetchall()[-1][0])  # 最近的日期

        except IndexError:
            print("无相关重复数据，可以直接写入")
            return info
        info = list(info)
        i = 0
        for i in range(len(info)):
            if info[i]['date'] == result:
                break
        return info[i + 1:]

    # 性能提升
    @staticmethod
    def programmerpool(func, pidlist):
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
