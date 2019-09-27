import datetime
from threading import Semaphore
from queue import Queue
from spyderpro.pool.threadpool import ThreadPool
from spyderpro.pool.redis_connect import RedisConnectPool
from spyderpro.pool.mysql_connect import ConnectPool
from spyderpro.function.weather_function.weather import Weather


class ManagerWeather:
    """
    缓存数据：
                key = "air:{0}".format(pid)
                value = {"pid": pid, "aqi": aqi, "pm2": pm2, "pm10": pm10, "co": co, "no2": no2, "o3": o3, "so2": so2,
                         "flag": 1, "lasttime": str(now)}
    """

    def __init__(self):
        self._redis_work = RedisConnectPool(10)  # redis连接池

    def manager_city_airstate(self):
        """
        更新空气质量数据
        :return:
        """
        semaphore = Semaphore(1)
        queue = Queue(1)  # 用来通知更新时间
        pool = ConnectPool(max_workers=10)  # mysql数据库连接池

        now = datetime.datetime.now()

        sql = "select pid,name from digitalsmart.citymanager"
        result = list(pool.select(sql))
        sql = "select lasttime from digitalsmart.airstate where flag=1"
        try:
            lasttime = pool.select(sql)[0][0]  # 最近更新时间
        except TypeError:
            lasttime = None
        weather = Weather()
        iter_citys_waether_objs = weather.get_city_weather_pid()  # 获取城市天气id
        city_map = dict()
        for obj in iter_citys_waether_objs:
            city_map[obj.city] = obj.aqi_pid
        thread_pool = ThreadPool(max_workers=10)
        count = len(result)  # 任务计数，0时通知更新时间
        time_interval = datetime.timedelta(minutes=60)
        for item in result:
            citypid = item[0]
            city = item[1]
            city_weather_pid = city_map[city]

            def fast(pid, weather_pid):
                aqi_state = weather.last_air_state(weather_pid)  # 请求数据

                aqi = aqi_state.aqi
                pm2 = aqi_state.pm2
                pm10 = aqi_state.pm10
                so2 = aqi_state.so2
                no2 = aqi_state.no2
                co = aqi_state.co
                o3 = aqi_state.o3
                # 缓存数据
                redis_key = "air:{0}".format(pid)
                value = {"pid": pid, "aqi": aqi, "pm2": pm2, "pm10": pm10, "co": co, "no2": no2, "o3": o3, "so2": so2,
                         "flag": 1, "lasttime": str(now)}
                self._redis_work.hashset(redis_key, value)
                self._redis_work.expire(name=redis_key, time_interval=time_interval)
                # 更新数据库
                sql_cmd = "insert into digitalsmart.airstate(pid, aqi, pm2, pm10, co, no2, o3, so2, flag, lasttime) " \
                          "value (%d,%d,%d,%d,%f,%d,%d,%d,%d,'%s')" % (pid, aqi, pm2, pm10, co, no2, o3, so2, 1, now)

                pool.sumbit(sql_cmd)
                semaphore.acquire()
                nonlocal count
                count -= 1  # 计数
                semaphore.release()
                if count == 0:  # 所有任务完成，通知数据库可以更新天气时间了
                    queue.put(1)
                return

            thread_pool.submit(fast, citypid, city_weather_pid)
        thread_pool.run()
        thread_pool.close()
        # 更新时间
        if lasttime:
            sql = "update digitalsmart.airstate set flag=0 where lasttime='{0}'".format(lasttime)
            queue.get()
            pool.sumbit(sql)
        pool.close()
        print("天气数据写入成功")


if __name__ == "__main__":
    from multiprocessing import Process

    m = ManagerWeather()
    Process(target=m.manager_city_airstate).start()
