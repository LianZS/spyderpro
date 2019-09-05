import requests
import re
import datetime
import json
import sys
import os
import pymysql
import time
from threading import Thread, Semaphore, Timer
from urllib.parse import urlencode

lock = Semaphore(12)


class Connect:

    def connect(self, par: str, url: str) -> dict:
        """网络连接
        :param par:正则表达式
        :param url:请求链接
        :return json
        """

        data = self.request.get(url=url, headers=self.headers)
        if data.status_code != 200:
            print("%s请求--error:网络出错" % url)
            raise ConnectionError('网络连接中断')
        try:
            if par is not None:
                result = re.findall(par, data.content.decode('gbk'), re.S)[0]
            else:
                result = data.text
        except UnicodeDecodeError:
            result = re.findall(par, data.text, re.S)[0]
        data = json.loads(result)
        assert isinstance(data, (dict, list))
        return data


class ParamTypeCheck():
    @staticmethod
    def type_check(param, param_type):
        """
        参数类型检查
        :rtype:
        :param param:
        :param param_type:
        :return:
        """
        assert isinstance(param, param_type), "the type of param is wrong"


class PlaceInterface(Connect, ParamTypeCheck):
    instance = None
    instance_flag: bool = False

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    # 获取所有省份
    def get_allprovince(self) -> list:
        """
        获取所有省份
        :return: list
        """
        href = "https://heat.qq.com/api/getAllProvince.php?sub_domain="
        par: str = None
        g = self.connect(par, href)
        data = [value["province"] for value in g]
        return data

    # 所有城市
    def get_allcity(self, province: str) -> list:
        """
        获取省份下所有城市
        :param province: 省份名
        :return: list[{"province": , "city":}，，]
        """
        # 这里不需要quote中文转url，因为后面的urlencode自动会转

        parameter = {
            "province": province,
            "sub_domain": ''
        }
        href = "https://heat.qq.com/api/getCitysByProvince.php?" + urlencode(parameter)
        par: str = None
        g = self.connect(par, href)
        results = [{"province": province, "city": value["city"]} for value in g]
        return results

    def get_regions_bycity(self, province: str, city: str) -> list:
        """
        获取城市下所有地区信息标识，关键id

        :type province: str
        :type city:str
        :param province:省份
        :param city:城市
        :return  list[{"place": , "id": },,,,]
        """
        self.type_check(province, str)
        self.type_check(city, str)
        parameter = {
            'province': province,
            'city': city,
            'sub_domain': ''
        }

        href = "https://heat.qq.com/api/getRegionsByCity.php?" + urlencode(parameter)

        par: str = None
        g = self.connect(par, href)
        datalist = list()
        for value in g:
            placename = value['name']  # 地点
            placeid = value["id"]  # id
            dic = {"place": placename, "id": placeid}
            datalist.append(dic)
        return datalist
        # range表示数据间隔，最小1,region_name是地点名字,id是景区pid


class PlaceFlow(PlaceInterface):
    """
    获取地区人口分布情况数据
    """

    def __init__(self, user_agent: str = None):

        if not PlaceFlow.instance_flag:
            PlaceFlow.instance_flag = True
            self.headers = dict()
            if user_agent is None:
                self.headers[
                    'User-Agent'] = 'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'

            else:
                self.headers['User-Agent'] = user_agent
            self.headers['Host'] = 'heat.qq.com'

            self.request = requests.Session()

    def request_heatdata(self, url: str):
        """
        网络请求
        :param url:
        :return:json
        """
        try:
            response = self.request.get(url=url, headers=self.headers)
        except Exception:
            lock.release()
            return None
        if response.status_code == 200:
            g = json.loads(response.text)
            return g
        else:
            return None

    def __get_heatdata_bytime(self, date: str, datetim: str, region_id: int):
        # self.type_check(region_id, int)
        paramer = {
            'region_id': region_id,
            'datetime': "".join([date, ' ', datetim]),
            'sub_domain': ''
        }

        url = "https://heat.qq.com/api/getHeatDataByTime.php?" + urlencode(paramer)
        g = self.request_heatdata(url)

        return g

    def count_headdata(self, ddate: str, ttime: str, region_id: int):
        """
        某一时刻的人数有多少
        :param date:日期：格式yyyy-mm-dd
        :param datetim:时间：格式hh:MM:SS
        :param region_id:地区唯一表示
        :return:总人数
        """

        g = self.__get_heatdata_bytime(ddate, ttime, region_id)
        if not g:
            return None
        count = sum(g.values())  # 总人数
        lock.release()
        user = 'root'
        password = 'lzs87724158'
        host = "localhost"
        port = 3306
        database = 'digitalsmart'
        ddate = int(ddate.replace("-", ""))
        try:
            db2 = pymysql.connect(host=host, user=user, password=password, database=database,
                                  port=port)
        except Exception:
            return
        cur2 = db2.cursor()
        sql = "insert into digitalsmart.scenceflow(pid, ddate, ttime, num) VALUE (%d,%d,'%s',%d)" % (
            region_id, ddate, ttime, count)
        cur2.execute(sql)
        db2.commit()
        db2.close()
    def complete_heatdata(self, date: str, datetim: str, region_id: int):
        """
           某一时刻的人数以及分布情况
           :param date:日期：格式yyyy-mm-dd
           :param datetime:时间：格式hh:MM:SS
           :param region_id:地区唯一表示
           :return:dict格式：{"lat": lat, "lng": lng, "num": num}->与中心经纬度的距离与相应人数
           """
        g = self.__get_heatdata_bytime(date, datetim, region_id)

        coords = map(self.deal_coordinates, g.keys())  # 围绕中心经纬度加减向四周扩展
        numlist = iter(g.values())

        for xy, num in zip(coords, numlist):
            lat = xy[0]
            lng = xy[1]
            yield {"lat": lat, "lng": lng, "num": num}

    @staticmethod
    def deal_coordinates(coord):
        if coord == ',':
            return (0, 0)
        escape = eval(coord)

        return escape


def get_count(region_id):
    datelist = dateiter(region_id)
    place = PlaceFlow()
    func = place.count_headdata
    for date, ttime, region_id in datelist:
        lock.acquire()
        Thread(target=func, args=(date, ttime, region_id,)).start()


def dateiter(region_id):
    date_time = datetime.datetime.now()
    today = date_time.date()
    hour = date_time.time().hour - 1
    if hour < 0:
        hour = 23
    inittime = datetime.datetime(today.year, today.month, today.day, hour, 0, 0)

    timedelta = datetime.timedelta(minutes=5)
    while 1:
        ttime = datetime.datetime.now().time()
        if inittime.year == today.year and inittime.month == today.month and inittime.day == today.day \
                and inittime.hour == ttime.hour and inittime.minute > ttime.minute:
            break

        yield str(inittime.date()), str(inittime.time()), region_id
        inittime = inittime + timedelta


base_dir = os.getcwd()
sys.path[0] = base_dir

if __name__ == "__main__":
    user = 'root'
    password = 'lzs87724158'
    host = "localhost"
    port = 3306
    database = 'digitalsmart'
    db = pymysql.connect(host=host, user=user, password=password, database=database,
                         port=port)
    cur = db.cursor()
    sql = "select pid from digitalsmart.scencemanager where flag=0 and type_flag=0"
    cur.execute(sql)
    data_result =list(cur.fetchall())
    while 1:

        for item in data_result:

            pid = item[0]
            print(pid)
            get_count(pid)
        time.sleep(3600)
