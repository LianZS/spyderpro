import requests
import json
import pymysql
from typing import Dict
from urllib.parse import urlencode


class LngLat:
    # 获取地区中心经纬度度
    def __init__(self):
        self.s = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/71.0.3578.98 Safari/537.36',
            'Host': 'apis.map.qq.com',

        }

    def get_city_lng_lat(self, city) -> Dict:  # 获取城市经纬度
        paramer = {
            "qt": "poi",
            "wd": city
        }
        url = "https://apis.map.qq.com/jsapi?" + urlencode(paramer)

        response = self.s.get(url=url, headers=self.headers)
        g = json.loads(response.text)
        location = g['detail']['area']
        try:
            lng = float(location['pointx'])
            lat = float(location['pointy'])
        except KeyError:
            print("error:{0}".format(city))
            return {
                city: 0
            }
        return {city: {
            "lng": lng,
            "lat": lat
        }}


if __name__ == "__main__":
    l = LngLat()
    db = pymysql.connect(host='localhost', user="root", password="lzs87724158",
                         database="digitalsmart", port=3306)
    cur = db.cursor()
    sql = "select name from digitalsmart.citymanager"
    cur.execute(sql)
    result = cur.fetchall()
    db.close()
    db = pymysql.connect(host='xxxxx', user="xxx", password="xxxx",
                         database="xxxx", port=3306)
    cur =db.cursor()
    for city, in result:
        localtion_lng_lat = l.get_city_lng_lat(city)
        if localtion_lng_lat[city] == 0:
            continue
        poin_lng = localtion_lng_lat[city]['lng']
        poin_lat = localtion_lng_lat[city]['lat']
        sql = "update  digitalsmart.citymanager set longitude={0} ,latitude={1} where name='{2}'".format(poin_lng,
                                                                                                         poin_lat, city)
        cur.execute(sql)
        db.commit()
