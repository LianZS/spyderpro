import datetime
from threading import Semaphore
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
from spyderpro.managerfunction.mysql_connect import ConnectPool
from spyderpro.function.weatherfunction.weather import Weather


class ManagerWeather:
    def __init__(self):
        self.lock = Semaphore(20)

    def manager_city_airstate(self):
        semaphore = Semaphore(1)
        queue = Queue(1)#用来通知更新时间
        pool = ConnectPool(max_workers=10)

        now = datetime.datetime.now()

        sql = "select pid,name from digitalsmart.citymanager"
        result = list(pool.select(sql))
        sql = "select lasttime from digitalsmart.airstate where flag=1"
        try:
            lasttime = pool.select(sql)[0][0]  # 最近更新时间
        except TypeError:
            lasttime = ''
        weather = Weather()
        city_map = weather.get_city_weather_pid()  # 获取城市天气id

        thread_pool = ThreadPoolExecutor(max_workers=10)
        count = len(result)
        i = 0
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

                sql_cmd = "insert into digitalsmart.airstate(pid, aqi, pm2, pm10, co, no2, o3, so2, flag, lasttime) " \
                          "value (%d,%d,%d,%d,%f,%d,%d,%d,%d,'%s')" % (pid, aqi, pm2, pm10, co, no2, o3, so2, 1, now)
                # pool.sumbit(sql_cmd)
                semaphore.acquire()
                nonlocal count
                count -= 1
                if count == 0:
                    queue.put(1)

                semaphore.release()

            thread_pool.submit(fast, citypid, city_weather_pid)
        #更新时间
        sql = "update digitalsmart.airstate set flag=0 where lasttime='{0}'".format(lasttime)
        queue.get()
        pool.sumbit(sql)


