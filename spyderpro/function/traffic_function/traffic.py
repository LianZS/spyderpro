import time
import json
import datetime
from typing import Iterator, List, Union
from spyderpro.pool.mysql_connect import ConnectPool

from spyderpro.data_requests.traffic.baidutraffic import BaiduTraffic
from spyderpro.data_requests.traffic.gaodetraffic import GaodeTraffic
from concurrent.futures import ThreadPoolExecutor
from spyderpro.port_connect.sql_connect import MysqlOperation
from spyderpro.data_requests.traffic.citytraffic import DayilTraffic, YearTraffic
from spyderpro.pool.redis_connect import RedisConnectPool


class Traffic(MysqlOperation):
    instance = None

    def __init__(self):
        self._redis_worker = RedisConnectPool(10)

    def __del__(self):
        del self._redis_worker

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

    def dealwith_daily_traffic(self, daily_traffic_instances: List[DayilTraffic], pid: int, mysql_pool: ConnectPool,
                               today: int, yesterday: int) -> List[DayilTraffic]:
        """
        重复数据处理
        :param daily_traffic_instances: 交通延迟数据对象包
        :param pid: 城市id
        :param mysql_pool: mysql连接词
        :param today: 今天日期,格式yyyymmdd
        :param yesterday: 昨天日期，格式yyyymmdd
        :return:
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
        :return:
        """
        traffic = None
        if citycode > 1000:
            traffic = GaodeTraffic()
        elif citycode < 1000:
            traffic = BaiduTraffic()
        road_instances = traffic.city_road_traffic_data(citycode)

        return road_instances

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
    def filter(dayiltraffic_instances: list, detailtime: str) -> List[DayilTraffic]:
        """
        过滤数据，清空已存在的数据
        :param dayiltraffic_instances:交通延迟指数对象包
        :param detailtime:具体时间段
        :return:list
        """
        for i in range(len(dayiltraffic_instances)):

            if dayiltraffic_instances[i].detailtime == detailtime:
                dayiltraffic_instances = dayiltraffic_instances[i + 1:]
                break
        return dayiltraffic_instances

    def get_and_write_dailytraffic_into_database(self, mysql_pool: ConnectPool, city_pid: int, cityname: str,
                                                 time_interval: datetime.timedelta):
        """

        :param mysql_pool: 连接池实例
        :param city_pid: 城市id
        :param cityname: 城市名
        :param time_interval: 缓存时间
        :return:
        """

        dailytraffic_instances = self.get_city_traffic(citycode=city_pid)  # 获取交通数据

        if dailytraffic_instances is None:
            print("pid:%d -- city:%s 没有数据" % (city_pid, cityname))

            return

        now = time.time()  # 现在的时间
        # 分好昨今以便分类过滤
        today = int(time.strftime('%Y%m%d', time.localtime(now)))
        yesterday = int(time.strftime('%Y%m%d', time.localtime(now - 3600 * 24)))
        dailytraffic_instances = list(dailytraffic_instances)
        # 缓存数据
        cache_traffic_data = dict()
        for dailytraffic in dailytraffic_instances:
            detailtime = dailytraffic.detailtime  # 时间点
            index = dailytraffic.index  # 拥堵指数
            cache_traffic_data[detailtime] = index
        # 缓存数据
        redis_key = "traffic:{0}".format(city_pid)

        self._redis_worker.hashset(name=redis_key, mapping=cache_traffic_data)
        self._redis_worker.expire(name=redis_key, time_interval=time_interval)
        # 过滤掉昨天和已经存在的数据
        filter_dailytraffic_instances = self.dealwith_daily_traffic(dailytraffic_instances, city_pid,
                                                                    mysql_pool, today,
                                                                    yesterday)

        # 数据写入mysql
        for dailytraffic in filter_dailytraffic_instances:
            sql_cmd = "insert into  digitalsmart.citytraffic(pid, ddate, ttime, rate)" \
                      " values('%d', '%d', '%s', '%f');" % (
                          city_pid, dailytraffic.date, dailytraffic.detailtime, dailytraffic.index)
            mysql_pool.sumbit(sql_cmd)

    def get_and_write_roadtraffic_into_database(self, mysql_pool: ConnectPool, city_pid: int, up_date: int,
                                                time_interval: datetime.timedelta):
        road_instances = self.road_manager(city_pid)  # 获取道路数据
        if road_instances is None:
            return
        for road in road_instances:
            region_id = road.region_id  # 标识
            roadname = road.roadname  # 路名
            speed = road.speed  # 速度
            direction = road.direction  # 方向
            bounds = road.bounds  # 经纬度数据集
            road_traffic_rate_list = road.road_index_data_list  # 拥堵指数集合
            road_traffic_time_list = road.time_data_list
            num = road.num
            data_pack = json.dumps({"num": num, "time": road_traffic_time_list, "data": road_traffic_rate_list})
            rate = road.rate  # 当前拥堵指数
            roadid = road.num  # 用排名表示道路id
            sql_insert = "insert into digitalsmart.roadtraffic(pid, roadname, up_date, speed, direction, " \
                         "bound, data,roadid,rate) VALUE (%d,'%s',%d,%f,'%s','%s','%s',%d,%f) " % (
                             region_id, roadname, up_date, speed, direction, bounds,
                             data_pack, roadid, rate)
            mysql_pool.sumbit(sql_insert)
            sql_cmd = "update  digitalsmart.roadmanager set up_date={0}  where pid={1} and roadid={2}" \
                .format(up_date, region_id, roadid)

            mysql_pool.sumbit(sql_cmd)  # 更新最近更新时间
            # 缓存数据
            # if data is None or bounds is None:  # 道路拥堵指数数据包请求失败情况下
            #     continue
            redis_key = "road:{pid}:{road_id}".format(pid=city_pid, road_id=roadid)
            cache_road_data_mapping = {
                "pid": city_pid, "roadname": roadname, "up_date": up_date, "speed": speed,
                "direction": direction, "bounds": bounds, "data": data_pack,
                "roadpid": roadid, "rate": rate
            }
            self._redis_worker.set(redis_key, str(cache_road_data_mapping))
            self._redis_worker.expire(name=redis_key, time_interval=time_interval)

    def get_and_write_yeartraffic_into_database(self, mysql_pool: ConnectPool, city_pid: int,
                                                time_interval: datetime.timedelta):
        yeartraffic_instances = self.yeartraffic(city_pid, mysql_pool)

        if len(yeartraffic_instances) == 0 or yeartraffic_instances is None:  # 此次请求没有数据
            return

        for yeartraffic in yeartraffic_instances:
            region_id = yeartraffic.region_id
            date = yeartraffic.date
            index = yeartraffic.index
            sql_cmd = "insert into digitalsmart.yeartraffic(pid, tmp_date, rate) VALUE (%d,%d,%f)" % (
                region_id, date, index)
            mysql_pool.sumbit(sql_cmd)
        sql = "select tmp_date,rate from digitalsmart.yeartraffic where pid={pid} and tmp_date>=20190101;".format(
            pid=city_pid)
        yeartraffic_data = mysql_pool.select(sql)
        cache_yeartraffic_mapping = dict()
        for tmp_date, rate in yeartraffic_data:
            cache_yeartraffic_mapping[tmp_date] = rate
        if not cache_yeartraffic_mapping:
            return
        redis_key = "yeartraffic:{pid}".format(pid=city_pid)
        self._redis_worker.set(redis_key, json.dumps(cache_yeartraffic_mapping))
        self._redis_worker.expire(name=redis_key, time_interval=time_interval)
