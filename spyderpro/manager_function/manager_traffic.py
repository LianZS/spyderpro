import datetime
from setting import *
from spyderpro.pool.threadpool import ThreadPool
from spyderpro.pool.mysql_connect import ConnectPool
from spyderpro.function.traffic_function.traffic import Traffic


class ManagerTraffic(Traffic):
    """
    缓存数据：
        日常交通拥堵延迟指数：key= "traffic:{0}".format(region_id),mapping ={"HH:MM:SS":rate,....}
        道路交通数据：key ="road:{pid}:{road_id}".format(pid=region_id, road_id=roadid)
                        value =str( {
                            "pid": pid, "roadname": roadname, "up_date": up_date, "speed": speed,
                            "direction": direction, "bounds": bound, "data": data,
                            "roadpid": roadid, "rate": rate
                        })
        季度交通数据：key = "yeartraffic:{pid}".format(pid=region_id) ,value={'yyyymmdd':rate,....}

    """

    def manager_city_traffic(self):
        """
        获取城市实时交通拥堵情况并写入数据库,半小时执行一次
        :return:
        """
        mysql_pool = ConnectPool(max_workers=7, host=host, user=user, password=password, port=port,
                                 database=database)
        sql = "select pid, name from digitalsmart.citymanager"
        data = mysql_pool.select(sql)
        # 千万不要开系统自带的线程池，占用的内存过大，而且每次线程退出后内存都没有释放，而是一直累加。使用自定义线程池，
        thread_pool = ThreadPool(max_workers=6)
        time_interval = datetime.timedelta(minutes=40)  # 缓存时间
        for item in data:
            city_pid = item[0]
            city_name = item[1]

            thread_pool.submit(self.get_and_write_dailytraffic_into_database, mysql_pool, city_pid, city_name,
                               time_interval)
        thread_pool.run()
        thread_pool.close()
        mysql_pool.close()
        print("城市交通数据挖掘完毕")

    def manager_city_road_traffic(self):
        """
        获取每个城市实时前10名拥堵道路数据-----10分钟执行一遍
        :return:
        """
        mysql_pool = ConnectPool(max_workers=7, host=host, user=user, password=password, port=port,
                                 database=database)
        up_date = int(datetime.datetime.now().timestamp())  # 记录最新的更新时间

        sql = "select pid from digitalsmart.citymanager"

        data = mysql_pool.select(sql)  # pid集合
        time_interval = datetime.timedelta(minutes=60)  # 缓存时间

        for item in data:  # 这里最好不要并发进行，因为每个pid任务下都有10个子线程，在这里开并发 的话容易被封杀

            city_pid = item[0]

            self.get_and_write_roadtraffic_into_database(mysql_pool, city_pid, up_date, time_interval)

        mysql_pool.close()

        print("城市道路交通数据挖掘完毕")

    def manager_city_year_traffic(self):
        time_interval = datetime.timedelta(days=1)
        mysql_pool = ConnectPool(max_workers=7, host=host, user=user, password=password, port=port,
                                 database=database)
        sql = "select pid from digitalsmart.citymanager"

        thread_pool = ThreadPool(max_workers=6)
        data = mysql_pool.select(sql)
        for item in data:
            yearpid = item[0]

            thread_pool.submit(self.get_and_write_yeartraffic_into_database, mysql_pool, yearpid, time_interval)
        thread_pool.run()
        thread_pool.close()
        mysql_pool.close()
        print("城市季度交通数据挖掘完毕")


if __name__ == "__main__":
    from multiprocessing import Process

    m = ManagerTraffic()
    Process(target=m.manager_city_road_traffic).start()
    Process(target=m.manager_city_traffic).start()
    Process(target=m.manager_city_year_traffic).start()
