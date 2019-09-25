import requests
import json
import datetime
from urllib.parse import urlencode
from typing import Iterator
from spyderpro.data_instances.keyword_obj import Mobile_Info


class MobileKeyWord:

    # *****注意，还未完成IOS相关数据获取
    def __init__(self, user_agent=None):
        """

        :type user_agent: str
        :param:user_agent：浏览器
        """

        self.request = requests.Session()

        self.headers = dict()

        if user_agent is None:
            self.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 ' \
                                         '(KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'

        else:
            self.headers['User-Agent'] = user_agent

    def get_mobile_type_rate(self, year: int, startmonth: int = None, endmonth: int = None, platform: int = 2) -> \
    Iterator[Mobile_Info]:
        """
        获取某个时段的中国境内各手机机型的占有率
        :rtype:iterable
        :param year:年份
        :param startmonth: 开始月份
        :param endmonth:结束月份
        :return :Iterator[Mobile_Info]
        platform=2表示安卓手机，1表示苹果
        """
        self.__type_check(year, startmonth, endmonth)

        return self.__mobile_rate(kw="机型", year=year, startmonth=startmonth, endmonth=endmonth, platform=2,
                                  terminaltype=2)

    def get_mobile_brand_rate(self, year: int, startmonth: int = None, endmonth: int = None) -> Iterator[Mobile_Info]:
        """
        获取某时段中国境内各手机品牌占用率
        :rtype: iterable
        :param year: 年份
        :param startmonth:开始月份
        :param endmonth: 结束月份
        :return :iterable[{"品牌": value['k'], "占有率": value['r']},,,,,,]

        """
        self.__type_check(year, startmonth, endmonth)

        return self.__mobile_rate(kw="品牌", year=year, startmonth=startmonth, endmonth=endmonth, platform=3,
                                  terminaltype=1)

    def get_mobile_resolution_rate(self, year: int, startmonth: int = None, endmonth: int = None) -> Iterator[
        Mobile_Info]:
        """
        获取某时段中国境内各手机分辨率占用率
        :rtype: iterable
        :param year: 年份
        :param startmonth:开始月份
        :param endmonth: 结束月份
        :return :iterable[{"分辨率": value['k'], "占有率": value['r']},,,,,,]        """
        self.__type_check(year, startmonth, endmonth)

        return self.__mobile_rate(kw="分辨率", year=year, startmonth=startmonth, endmonth=endmonth, platform=2,
                                  terminaltype=3)

    def get_mobile_system_rate(self, year: int, startmonth: int = None, endmonth: int = None,platform=2) -> Iterator[Mobile_Info]:
        """
        获取某时段中国境内各手机系统版本占用率
        :rtype: iterable
        :param year: 年份
        :param startmonth:开始月份
        :param endmonth: 结束月份
        :return :iterable[{"操作系统": value['k'], "占有率": value['r']},,,,,,]

        """
        self.__type_check(year, startmonth, endmonth)

        return self.__mobile_rate(kw="操作系统", year=year, startmonth=startmonth, endmonth=endmonth, platform=platform,
                                  terminaltype=4)

    def get_mobile_operator_rate(self, year: int, startmonth: int = None, endmonth: int = None) -> Iterator[
        Mobile_Info]:
        """
        获取某时段中国境内各手机运营商占用率
        :rtype: list
        :param year: 年份
        :param startmonth:开始月份
        :param endmonth: 结束月份
        :return :iterable[{"运营商": value['k'], "占有率": value['r']},,,,,,]

        """
        self.__type_check(year, startmonth, endmonth)

        return self.__mobile_rate(kw="运营商", year=year, startmonth=startmonth, endmonth=endmonth, platform=2,
                                  terminaltype=5)

    def get_mobile_network_rate(self, year: int, startmonth: int = None, endmonth: int = None) -> Iterator[Mobile_Info]:
        """
        获取某时段中国境内各手机网络占用率
        :rtype: ite
        :param year: 年份
        :param startmonth:开始月份
        :param endmonth: 结束月份
        :return :iterable[Mobile_Info("网络": value['k'], "占有率": value['r']),,,,,,]

        """
        self.__type_check(year, startmonth, endmonth)

        return self.__mobile_rate(kw="网络", year=year, startmonth=startmonth, endmonth=endmonth, platform=2,
                                  terminaltype=6)

    def __mobile_rate(self, kw: str, terminaltype: int, platform: int, year: int, startmonth: int = None,
                      endmonth: int = None) -> Iterator[Mobile_Info]:
        """

        :param terminaltype: 网络请求类型
        :param platform:网络请求类型
        :param year:年份
        :param startmonth:开始月份
        :param endmonth:结束月份
        :rtype: iterable[obj]
        """
        monthlist = []  # 请求列表
        if year < 2014:
            raise TypeError("超过最低年限2014")
        if startmonth > 12 or startmonth < 1:
            raise TypeError("月份出错")
        if endmonth is None and startmonth is not None:
            date = datetime.date(year, startmonth, 1)
            monthlist.append(date)
        elif startmonth is None:
            raise TypeError("startmonth不能为空")
        elif startmonth > endmonth:
            raise TypeError("startmonth不能大于endmonth")
        else:
            seq = endmonth - startmonth + 1
            for i in range(seq):
                date = datetime.date(year, startmonth + i, 1)
                monthlist.append(date)

        pre_url = 'http://mi.talkingdata.com/terminal.json?'
        for date in monthlist:
            query_string_parameters = {
                "dateType": 'm',
                'date': date,
                'platform': platform,
                'terminalType': terminaltype
            }
            url = pre_url + urlencode(query_string_parameters)

            response = self.request.get(url=url, headers=self.headers)
            if response.status_code != 200:
                raise ConnectionError("网络请求"
                                      "出问题")
            result = json.loads(response.text)
            for value in result:
                info = Mobile_Info(kw, value['k'], value['r'], date)
                yield info

    def __type_check(self, year, startmonth, endmonth):
        assert isinstance(year, int), 'year is not type of int'
        assert isinstance(startmonth, int), 'startmonth is not type of int'
        if endmonth is not None:
            assert isinstance(endmonth, int), 'endmonth is not type of int'
# d = MobileKeyWord().get_mobile_network_rate(2018,5,8)
# for i in d:
#     print(i.type_kw,i.value)
