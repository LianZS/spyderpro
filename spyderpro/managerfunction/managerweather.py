import datetime
from threading import Thread, Semaphore
from queue import Queue
from setting import *
from spyderpro.function.weatherfunction.weather import Weather


class ManagerWeather:
    def __init__(self):
        self.lock = Semaphore(10)
        self.connectqueue = Queue(6)  # 最多十个数据库连接
        for i in range(6):
            self.connectqueue.put(pymysql.connect(host=host, user=user, password=password, database=database,
                                                  port=port))

    def manager_city_airstate(self):
        db = pymysql.connect(host=host, user=user, password=password, database=database,
                             port=port)
        now = datetime.datetime.now()

        cur = db.cursor()
        sql = "select pid,name from digitalsmart.citymanager"
        cur.execute(sql)
        result = cur.fetchall()

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
                db_link = self.connectqueue.get()
                cur_link = db_link.cursor()
                sql = "insert into digitalsmart.airstate(pid, aqi, pm2, pm10, co, no2, o3, so2, flag, lasttime) " \
                      "value (%d,%d,%d,%d,%f,%d,%d,%d,%d,'%s')"%(pid,aqi,pm2,pm10,co,no2,o3,so2,1,now)
                try:
                    cur_link.execute(sql)
                    db_link.commit()
                except Exception as e:
                    db_link.rollback()
                self.connectqueue.put(db_link)
                self.lock.release()

            self.lock.acquire()
            Thread(target=fast, args=(citypid,city_weather_pid,)).start()


