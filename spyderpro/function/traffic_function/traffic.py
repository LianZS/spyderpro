import time
from typing import Iterator, List, Union
from spyderpro.pool.mysql_connect import ConnectPool

from spyderpro.data_requests.traffic.baidutraffic import BaiduTraffic
from spyderpro.data_requests.traffic.gaodetraffic import GaodeTraffic
from concurrent.futures import ThreadPoolExecutor
from spyderpro.port_connect.sql_connect import MysqlOperation
from spyderpro.data_requests.traffic.citytraffic import DayilTraffic, YearTraffic


class Traffic(MysqlOperation):
    instance = None

    @classmethod
    def dailycitytraffic(cls, citycodelist: list):
        while True:
            if cls.instance is None:
                cls.instance = super().__new__(cls)
            cls.instance.programmerpool(cls.instance.get_city_traffic, citycodelist)

    def get_city_traffic(self, citycode: int) -> Union[None, Iterator[DayilTraffic]]:
        """
        获取城市实时交通拥堵指数数据
        :param citycode:
        :return:List[TrafficClass]
        """
        if citycode > 1000:
            traffic = GaodeTraffic()

        elif 0 < citycode < 1000:

            traffic = BaiduTraffic()
        else:
            return None

        daily_traffic_instances = traffic.city_daily_traffic_data(citycode)
        if daily_traffic_instances is None:
            return None

        return daily_traffic_instances

    def dealwith_daily_traffic(self, daily_traffic_instances, pid, mysql_pool: ConnectPool, today, yesterday) -> List[DayilTraffic]:
        """
        重复数据处理
        :param info: 数据包
        :param pid: 城市id
        :param mysql_pool: mysql连接词
        :param today: 今天日期
        :param yesterday: 昨天日期
        :return: list
        """
        # 将昨天的数据全部剔除
        daily_traffic_instances = list(daily_traffic_instances)
        for i in range(len(daily_traffic_instances)):
            if daily_traffic_instances[i].date > yesterday:
                objs = daily_traffic_instances[i:]
                break

        "下面是过滤今天已经存在的数据---今天重复的数据剔除"
        sql = "select ttime from  digitalsmart.citytraffic where pid={0} and ddate={1} order by ttime".format(pid,
                                                                                                              today)
        data = mysql_pool.select(sql)

        if len(data):
            ttime = str(data[len(data) - 1][0]) if len(str(data[len(data) - 1][0])) == 8 else "0" + str(
                data[len(data) - 1][0])  # 最新的时间  xx:xx:xx
        else:
            ttime = "-1:00:00"  # 今天还未录入数据的情况
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
        result = g.city_road_traffic_data(citycode)

        return result

    def yeartraffic(self, yearpid: int, mysql_pool: ConnectPool):

        g = None
        if yearpid > 1000:
            g = GaodeTraffic()
        elif yearpid < 1000:
            g = BaiduTraffic()
        result = g.city_year_traffic_data(yearpid)
        if result is None:
            return None
        result = self.__dealwith_year_traffic(result, yearpid, mysql_pool,
                                              lastdate=int(time.strftime("%Y%m%d",
                                                                         time.localtime(time.time() - 24 * 3600))))
        return result

    def __dealwith_year_traffic(self, info: Iterator, pid: int, mysql_pool: ConnectPool, lastdate: int) -> List[
        YearTraffic]:
        sql = "select tmp_date from digitalsmart.yeartraffic where pid={0} and tmp_date>= {1} order by tmp_date".format(
            pid, lastdate)
        data = mysql_pool.select(sql)

        if len(data) == 0:
            return list(info)
        last_date: int = data[-1]  # 最近的日期

        info = list(info)
        if len(info) == 0:  # 请求失败情况下
            return []
        i = -1
        for i in range(len(info)):
            if info[i].date == last_date:
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
    def filter(info: list, detailtime: str) -> List[DayilTraffic]:
        """
        过滤数据，清空已存在的数据
        :param info:数据包
        :param detailtime:具体时间段
        :return:list
        """
        for i in range(len(info)):

            if info[i].detailtime == detailtime:
                info = info[i + 1:]
                break
        return info

    # def find_name(self, citycode: int, db) -> str:
    #     """
    #     查询城市名字
    #     :param citycode:  城市id
    #     :param db: 数据库实例
    #     :return: str ->城市名
    #     """
    #     sql = "select  name from trafficdatabase.MainTrafficInfo where cityCode=" + str(citycode) + ";"
    #     cursor = db.cursor()
    #     cityname = None
    #     try:
    #         cursor.execute(sql)
    #         db.commit()
    #         cityname = cursor.fetchone()[0]
    #
    #     except TypeError as e:
    #         print("数据库执行出错:%s" % e)
    #         db.rollback()
    #         cursor.close()
    #     return cityname
