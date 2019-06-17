import pymysql
from spyderpro.Connect.MysqlConnect import MysqlOperation
from spyderpro.WeatherModel.WeatherLishi import WeatherHistory
from spyderpro.FunctionMain.setting import *


class WeatherOperation(MysqlOperation):
    def __init__(self):
        pass

    def wirte_province(self):
        """
        将数据写入province数据库里
        :return:
        """
        db = pymysql.connect(host=host, user=user, password=password, database=weatherdatabase,
                             port=port)
        db.connect()
        result = self.get_provinces()
        for vlaue, pid in zip(result, range(1, len(result) + 1)):
            province = vlaue['province']
            href = vlaue['url']
            sql = "insert into weather.province (name, provincepid,href) values ('%s','%d','%s')" % (
                province, pid, href)
            # sql = "update weather.province set href='" + href + "' where name='" + province + "'"
            flag = self.loaddatabase(db=db, sql=sql)
            if not flag:
                print("写入失败")

    def write_citys(self, province: str):
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

    def get_histroy_hrefs(self, city):
        """
        获取该城市下所有
        :param url:
        :return:
        """
        db = pymysql.connect(host=host, user=user, password=password, database=weatherdatabase,
                             port=port)
        db.connect()

        sql = "select href,citypid from weather.city where name='" + city + "'"
        cursor = self.get_cursor(db=db, sql=sql)
        find = cursor.fetchone()
        url = find[0]
        pid = find[1]
        history = WeatherHistory()
        data = history.get_city_all_partition(url)
        return {"data": data, "pid": pid}

    def write_historyhrefs(self, city: str):
        db = pymysql.connect(host=host, user=user, password=password, database=weatherdatabase,
                             port=port)
        db.connect()
        result = self.get_histroy_hrefs(city)
        pid = result['pid']
        data = result['data']
        for href in data:
            sql = "insert into weather.historylist (pid_id,href) values ('%d','%s')" % (
                pid, href)
            flag = self.loaddatabase(db=db, sql=sql)
            if not flag:
                print("写入失败")


if __name__ == "__main__":
    w = WeatherOperation()
    # w.wirte_province()
    # for province in w.get_provinces():
    #     w.write_citys(province['province'])

    # w.get_histroy_hrefs('昌平 ')
