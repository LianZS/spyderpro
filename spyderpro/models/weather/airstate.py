import requests
import re
from typing import Dict
from bs4 import BeautifulSoup
from spyderpro.instances.weather import AQIState


class AirState:
    instanceflag = 0
    instance = None

    def __new__(cls, *args, **kwargs):
        if AirState.instance is None:
            obj = super().__new__(cls)
            AirState.instance = obj
        return AirState.instance

    def __init__(self, use_agent=None):
        if AirState.instanceflag == 0:

            self.request = requests.Session()
            if use_agent is None:
                self.headers = {
                    'Host': 'tianqi.2345.com',
                    'User-Agent': 'Mozilla/5.0 (Macinto¬sh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                                  'Chrome/71.0.3578.98 Safari/537.36'

                }
            AirState.instanceflag = 1

    def get_city_air_pid(self)->Dict:
        # 获取每个城市的专属id
        response = self.request.get(url="http://tianqi.2345.com/js/citySelectData.js", headers=self.headers)
        if response.status_code != 200:
            return None
        city_dic = dict()
        city_map = re.findall("\s(\D+)-(\d+)", response.text)
        for item in city_map:
            city = item[0]
            pid = int(item[1])
            city_dic[city] = pid
        return city_dic

    def get_city_air_state(self, citypid) -> AQIState:
        # 获取城市最新的空气数据
        href = "http://tianqi.2345.com/t/his/" + str(citypid) + "his.js"
        response = self.request.get(url=href, headers=self.headers)
        soup = BeautifulSoup(response.text, 'lxml')
        aqi = int(soup.find(name="span").text)  # AQI  指数
        href = "http://tianqi.2345.com/air-" + str(citypid) + ".htm"

        response = self.request.get(url=href, headers=self.headers)
        soup = BeautifulSoup(response.text, 'lxml')
        ul = soup.find(name="ul", attrs={"class": "clearfix"})
        air_map = dict()
        try:
            for item in ul.find_all(name="li"):
                air_type = item.find(name="div", attrs={"class": 'name'}).text  # 颗粒种类
                air_value = item.find(name="div", attrs={"class": 'value'}).text  # 含量
                air_value = re.findall("(\d+)\D", air_value)
                if len(air_value) >= 2:
                    air_value = float(air_value[1]) / 10
                else:
                    air_value = int(air_value[0])
                air_map[air_type] = air_value
        except AttributeError:
            return AQIState(aqi,0,0,0,0,0,0)
        pm2 = air_map["PM2.5"]
        pm10 = air_map['PM10']
        so2 = air_map['二氧化硫']
        no2 = air_map['二氧化氮']
        co = air_map['一氧化碳']
        o3 = air_map['臭氧']
        return AQIState(aqi, pm2, pm10, so2, no2, co, o3)



