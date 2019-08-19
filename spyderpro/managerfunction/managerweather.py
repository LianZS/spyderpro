import datetime
from threading import Thread, Semaphore
from queue import Queue
from setting import *
from spyderpro.function.weatherfunction.weather import Weather


class ManagerWeather:
    def __init__(self):
        self.lock = Semaphore(20)

    def manager_city_airstate(self):
        queue = Queue(1)
        db = pymysql.connect(host=host, user=user, password=password, database=database,
                             port=port)
        now = datetime.datetime.now()

        cur = db.cursor()
        sql = "select pid,name from digitalsmart.citymanager"
        cur.execute(sql)
        result = cur.fetchall()
        sql = "select lasttime from digitalsmart.airstate where flag=1"
        cur.execute(sql)
        try:
            lasttime = cur.fetchone()[0]  # 最近更新时间
        except TypeError:
            lasttime =''
        weather = Weather()
        city_map = weather.get_city_weather_pid()
        for item in result:
            citypid = item[0]
            city = item[1]
            city_weather_pid = city_map[city]

            def fast(pid, weather_pid):
                aqi_state = weather.last_air_state(weather_pid)

                aqi = aqi_state.aqi
                pm2 = aqi_state.pm2
                pm10 = aqi_state.pm10
                so2 = aqi_state.so2
                no2 = aqi_state.no2
                co = aqi_state.co
                o3 = aqi_state.o3

                sql = "insert into digitalsmart.airstate(pid, aqi, pm2, pm10, co, no2, o3, so2, flag, lasttime) " \
                      "value (%d,%d,%d,%d,%f,%d,%d,%d,%d,'%s')" % (pid, aqi, pm2, pm10, co, no2, o3, so2, 1, now)
                queue.put(1)
                try:
                    cur.execute(sql)
                    db.commit()
                except Exception as e:
                    db.rollback()
                    db.commit()
                queue.get()
                self.lock.release()

            self.lock.acquire()
            Thread(target=fast, args=(citypid, city_weather_pid,)).start()
        sql = "update digitalsmart.airstate set flag=0 where lasttime='{0}'".format(lasttime)
        queue.put(1)
        try:
            cur.execute(sql)
            db.commit()
        except Exception :
            db.rollback()
            db.commit()
        queue.get()



