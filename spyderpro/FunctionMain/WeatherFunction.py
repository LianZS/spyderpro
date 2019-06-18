import pymysql
from spyderpro.Connect.MysqlConnect import MysqlOperation
from spyderpro.WeatherModel.WeatherLishi import WeatherHistory
from spyderpro.FunctionMain.setting import *
from concurrent import futures


class WeatherOperation(MysqlOperation):
    def __init__(self):
        self.excutor = futures.ProcessPoolExecutor(max_workers=4)

    def get_and_wirte_province(self):
        """
        将数据写入province数据库里
        :return:
        """
        db = pymysql.connect(host=host, user=user, password=password, database=weatherdatabase,
                             port=port)
        db.connect()
        result = self.get_provinces()
        flag = self.write_province(db=db, result=result)
        if flag:
            print("success")
        else:
            print("fail")

    def write_province(self, db, result):
        for vlaue, pid in zip(result, range(1, len(result) + 1)):
            province = vlaue['province']
            href = vlaue['url']
            sql = "insert into weather.province (name, provincepid,href) values ('%s','%d','%s')" % (
                province, pid, href)
            # sql = "update weather.province set href='" + href + "' where name='" + province + "'"
            flag = self.loaddatabase(db=db, sql=sql)
            if not flag:
                print("写入失败")
        return True

    def get_and_write_citys(self, province: str):
        """
        将数据写入city数据库里
        :param province:
        :return:
        """
        db = pymysql.connect(host=host, user=user, password=password, database=weatherdatabase,
                             port=port)
        db.connect()
        dic: dict = self.get_citys(province)
        pid = dic['pid']
        data = dic['data']
        citypid = pid * 12345 + 13  # 构造id规律
        for value in data:
            city = value['city']
            href = value['url']
            sql = "insert into weather.city (pid_id,name, citypid,href) values ('%d','%s','%d','%s')" % (
                pid, city, citypid, href)
            # sql = "update weather.city set href='" + href + "' where citypid=" + str(citypid)

            citypid += 1
            flag = self.loaddatabase(db=db, sql=sql)
            if not flag:
                print("写入失败")

    @staticmethod
    def get_provinces():
        """
        获取省份数据[{"province":,"url":}]
        :return:
        """
        history = WeatherHistory()
        result = history.get_province_link()
        return result

    def get_citys(self, province: str):
        """
        获取省份下所有城市
        :param province:
        :return:
        """
        db = pymysql.connect(host=host, user=user, password=password, database=weatherdatabase,
                             port=port)
        db.connect()
        sql = "select href,provincepid from weather.province where name='" + province + "'"
        cursor = self.get_cursor(db=db, sql=sql)
        find = cursor.fetchone()
        url = find[0]
        pid = find[1]
        data = WeatherHistory().get_city_past_link(url)
        return {"data": data, "pid": pid}

    @staticmethod
    def get_histroy_hrefs(url: str, pid: int):
        """
        获取该城市下所有月份的链接
        :param url:
        :return:{"data": data->list, "pid": pid}
        """
        history = WeatherHistory()
        try:
            data = history.get_city_all_partition(url)
        except Exception:
            return None
        return {"data": data, "pid": pid}

    def write_historyhrefs(self, data: list, pid: int):
        """
        将链接写入数据库
        :param data:数据列表
        :return bool
        """

        db = pymysql.connect(host=host, user=user, password=password, database=weatherdatabase,
                             port=port)
        db.connect()

        for href in data:
            sql = "insert into weather.historylist (pid_id,href) values ('%d','%s')" % (
                pid, href)
            flag = self.loaddatabase(db=db, sql=sql)
            if not flag:
                print("写入失败")

        db.close()
        return True

    def get_and_write_historyhref(self):
        """
        获取历史数据链接并写入数据库
        :return:
        """
        db = pymysql.connect(host=host, user=user, password=password, database=weatherdatabase,
                             port=port)
        db.connect()

        sql = "select name,citypid,href from weather.city"
        cursor = self.get_cursor(db, sql)
        all = cursor.fetchall()
        cursor.close()
        db.close()
        urllist = [item[2] for item in all]
        pidlist = [item[1] for item in all]
        tasks = self.excutor.map(self.get_histroy_hrefs, urllist, pidlist,
                                 chunksize=4)
        for task in tasks:
            data = task['data']
            pid = task['pid']
            flag = self.write_historyhrefs(data=data, pid=pid)
            if not flag:
                print("%d写入失败" % pid)
            print("%d ok" % pid)

    @staticmethod
    def get_weather_state(url: str, pid: int):
        """
        获取历史天气数据
        :param url:
        :return:{"data": data, "pid": pid}
        """

        history = WeatherHistory()
        data = history.get_weather_detail(url)
        return {"data": data, "pid": pid}

    def write_weather_state(self, data: list, pid: int):
        """
        历史天气数据写入数据库
        """
        db = pymysql.connect(host=host, user=user, password=password, database=weatherdatabase,
                             port=port)
        db.connect()
        for status in data:
            date = status['date']
            state = status['state']
            temperature = status['temperature']
            wind = status['wind']
            sql = "insert into weather.history (date, state, temperature, wind, pid_id) " \
                  "value('%s','%s','%s','%s','%d')" % (date, state, temperature, wind, pid)
            flag = self.loaddatabase(db=db, sql=sql)
            if not flag:
                print("写入失败")

        db.close()
        return True

    def get_and_write_weather_state(self):
        db = pymysql.connect(host=host, user=user, password=password, database=weatherdatabase,
                             port=port)
        db.connect()
        sql = "select pid_id,href from weather.historylist "
        cursor = self.get_cursor(db, sql)
        all = cursor.fetchall()
        pids = [item[0] for item in all]
        hrefs = [href[1] for href in all]
        tasks = self.excutor.map(self.get_weather_state, hrefs, pids, chunksize=4)
        for task in tasks:
            data = task['data']
            pid = task['pid']
            flag = self.write_weather_state(data, pid)
            if not flag:
                print("%d写入失败" % pid)
            print("%d ok" % pid)


if __name__ == "__main__":
    w = WeatherOperation()
    w.get_and_write_weather_state()
