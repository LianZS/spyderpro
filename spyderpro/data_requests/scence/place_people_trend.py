import time
import requests
from datetime import datetime, timedelta

from urllib.parse import urlencode
from typing import Iterator
from spyderpro.data_instances.lbs import Trend
from spyderpro.data_requests.scence._place_people_interface import _PlacePeopleParentInterface


class PlaceTrend(_PlacePeopleParentInterface):
    """获取位置流量趋势"""

    def __init__(self, date_begin: str, date_end: str, intervallong: int = 5, user_agent: str = None):
        """
        时间段最长15天，最小时间间隔是1分钟range，开始时间最早2016-07-18
        :type date_begin: str
        :type date_end:str
        :type intervallong:int
        :param intervallong:数据间隔时间，最小为1分钟

        :param date_begin:开始搜索时间,格式yyyy-mm-dd
        :param date_end:结束搜索时间,格式yyyy-mm-dd
        :param user_agent:浏览器头
        """

        self.yyyy_mm_dd_date_begin = date_begin
        self.yyyy_mm_dd_date_end = date_end
        self.intervallong = intervallong
        if not PlaceTrend.bool_instance_flag:
            PlaceTrend.bool_instance_flag = True
            self.headers = dict()
            if user_agent is None:
                self.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) ' \
                                             'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 ' \
                                             'Safari/537.36'

            else:
                self.headers['User-Agent'] = user_agent
            self.headers['Host'] = 'heat.qq.com'

            self.request = requests.Session()

    def get_trend(self, region_name: str, pid: int, predict: bool = False) -> Iterator[Trend]:
        """

        获取地点的位置流量趋势指数，返回list({地点, 日期，趋势列表},,,)
        :param region_name:  地名
        :param pid: 地点id

        :return  Iterator[Trend]
        """
        # 请求参数
        dict_parameter = {
            'region': pid,
            'date_begin': self.yyyy_mm_dd_date_begin,
            'date_end': self.yyyy_mm_dd_date_end,
            'range': self.intervallong,
            'predict': predict  # 是否获取预测数据,若为true，预测那天的键需要加上「预测」两字
        }
        # 请求链接
        str_href = "https://heat.qq.com/api/getLocation_uv_percent_new.php?" + urlencode(dict_parameter)
        par: str = None
        # 获取返回数据
        dict_data = self.connect(par, str_href)
        # 获取间隔日期 ----仅限于最大周期15天
        intervallong = timedelta(minutes=5)
        # # 时间从00：00：00开始计算，不管日期，这里只是为了取时间
        datetime_starttime = datetime(2019, 1, 1, 0, 0, 0)
        # 获取用户需要请求的日期时间
        for date in self._date_iterator():
            for index, detail_time in zip(dict_data[date],
                                          [str((datetime_starttime + intervallong * i).time()) for i in
                                           range(len(dict_data[date]))]):
                if index == "null":
                    break
                # 趋势结构体
                trend = Trend(pid=pid, place=region_name, date=int(date.replace("-", "")), index=float(index),
                              detailtime=detail_time)
                yield trend

    def _date_iterator(self) -> Iterator[str]:
        """
        解析用户需要请求的时间，将yyyymmdd转为 yyyy-mm-dd格式
        :return:日期迭代器
        """
        # yyyymmdd转为yyyy-mm-dd格式
        str_format_date = time.strptime(self.yyyy_mm_dd_date_begin, "%Y-%m-%d")
        # 时间间隔
        timedelta_intervallong = timedelta(days=1)
        # 初始化时间
        init_date = datetime(str_format_date.tm_year, str_format_date.tm_mon, str_format_date.tm_mday)
        while 1:
            yyyy_mm_dd_date = str(init_date.date())
            if yyyy_mm_dd_date == self.yyyy_mm_dd_date_end:
                break
            yield yyyy_mm_dd_date
            # 下一刻时间
            init_date = init_date + timedelta_intervallong
