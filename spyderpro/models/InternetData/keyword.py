import requests
import json
import time
import re
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from spyderpro.portconnect.internetconnect import Connect
from spyderpro.instances.keyword_obj import BaiduKeyWordObject, WechatKeyWordObject, SougouKeyWordObject
from typing import Iterable, Iterator


class KeyWord(Connect):
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

    def baidu_get_keyword_search_index(self, keyword: str, baidu: bool = True,
                                       pc: bool = True, modile: bool = True) -> BaiduKeyWordObject:

        """
        能够获取百度浏览器的关键词搜索频率-----第一种方案


        :param keyword:搜索关键词
        :param baidu: 是否返回百度相关搜索量
        :param pc: 是否返回pc端相关搜索量
        :param modile: 是否返回移动端相关搜索量
        :return:iter([baidu_instance, sougou_instance])
        """

        url = "http://index.chinaz.com/index/" + keyword
        par = "eval\\((.*?)\\);"
        g: dict = self.connect(par, url)
        if len(g['baidu']) == 0:
            return None
        for baidu_value, weixin_value, haosou_value, sougou_value in zip(g['baidu'], g['weixin'], g['haosou'],
                                                                         g['sogou']):  # 只遍历一次
            baidu_update = baidu_value.get("update")  # 百度最近关键词收编时间
            baidu_all = iter(baidu_value['all']['index'])  # 百度30天内总的搜索次数
            baidu_pc = iter(baidu_value['pc']['index'] if pc else None)  # 百度电脑端搜索量
            baidu_mobile = iter(baidu_value['mobile']['index'] if modile else None)  # 百度手机端搜索量
            baidu_instance = BaiduKeyWordObject("baidu", baidu_all, baidu_pc, baidu_mobile,
                                                baidu_update) if baidu else None

            # weixin_update = weixin_value.get("update")  # 微信最近关键词收编时间
            # weixin_all = iter(weixin_value['all']['index'])  # 微信30天内总的搜索次数
            # wetchat_instance = KeyWordObject('weixin', weixin_all, None, None, weixin_update) if weixin else None
            # # haosou_update = haosou_value.get("update")  # 360最近关键词收编时间
            # # haosou_all = iter(haosou_value['all']['index'])  # 360 30天内总的搜索次数
            # # haosou_pc = iter(haosou_value['pc']['index'] if pc else None)  # 360 电脑端搜索量
            # # haosou_mobile = iter(haosou_value['mobile']['index'] if modile else None)  # 360手机端搜索量
            # sougou_update = sougou_value.get("update")  # 搜狗最近关键词收编时间
            # sougou_all = iter(sougou_value['all']['index'])  # 搜狗30天内总的搜索次数
            # sougou_pc = iter(sougou_value['pc']['index'] if pc else None)  # 搜狗电脑端搜索量
            # sougou_mobile = iter(sougou_value['mobile']['index'] if modile else None)  # 搜狗手机端搜索量
            # # haosou_instance = KeyWordObject("haosou", haosou_all, haosou_pc, haosou_mobile,
            # #                                 haosou_update) if haosou else None
            # sougou_instance = KeyWordObject("sougou", sougou_all, sougou_pc, sougou_mobile,
            #                                 sougou_update) if sougou else None
            # yield iter([baidu_instance, wetchat_instance, sougou_instance])
            print(keyword,"baidu search is search")
            return baidu_instance

    def wechat_get_keyword_search_index(self, keyword, startDate, endDate) -> Iterator[WechatKeyWordObject]:
        """
        要求endDate-startDate=0
        :param keyword:
        :param startDate: yyyymmdd
        :param endDate: yyyymmdd
        :return:
        """
        parameter = {
            'kwdNamesStr': keyword,
            'startDate': startDate,
            'endDate': endDate,
            'dataType': 'MEDIA_WECHAT',
            'queryType': 'INPUT',
        }
        url = "http://zhishu.sogou.com/getDateData?" + urlencode(parameter)
        response = self.request.get(url=url, headers=self.headers)

        if response.status_code == 404:
            print("404 retry")
            response = self.request.get(url=url, headers=self.headers)
        if response.status_code != 200:
            print(keyword)
            return None
        try:
            data = json.loads(response.text)['data']['pvList'][0]
        except IndexError as e:
            print(e)
            print(keyword, 'fail')
            return None
        print(keyword, 'wechat search success')

        for item in data:
            date = int(item['date'])
            value = item['pv']
            yield WechatKeyWordObject("wechat", int(value), date)

    def sougou_get_keyword_search_index(self, keyword: str, startDate: int, endDate: int) -> Iterator[
        SougouKeyWordObject]:
        """
        要求endDate-startDate=2

        :param keyword:
        :return:
        """
        parameter = {
            'kwdNamesStr': keyword,
            'startDate': startDate,
            'endDate': endDate,
            'dataType': 'SEARCH_ALL',
            'queryType': 'INPUT',
        }
        url ='http://zhishu.sogou.com/getDateData?'+urlencode(parameter)
        # url = "http://zhishu.sogou.com/index/searchHeat?" + urlencode(parameter)
        # response = self.request.get(url=url, headers=self.headers)
        # if response.status_code == 404:
        #     print("error")
        #     return None
        #
        # response = re.sub("\s", "", response.text)
        #
        # result = re.findall("data=(.*)\Wroot", response)
        # if not len(result):
        #     print("retry")
        #     response = self.request.get(url=url, headers=self.headers)
        #     response = re.sub("\s", "", response.text)
        #     result = re.findall("data=(.*)\Wroot", response)
        # g = None
        # try:
        #     g = json.loads(result[0])
        # except Exception as e:
        #     print(e)
        #     return None
        # for item in g['pvList'][0]:  # 一个月的数据
        #     date = int(item['date'])
        #     value = item['pv']
        #     yield SougouKeyWordObject("sougou", int(value), date)
        response = self.request.get(url=url, headers=self.headers)

        if response.status_code == 404:
            print("404 retry")
            response = self.request.get(url=url, headers=self.headers)
        if response.status_code != 200:
            print(keyword)
            return None
        try:
            data = json.loads(response.text)['data']['pvList'][0]
        except IndexError as e:
            print(e)
            print(keyword, 'fail')
            return None
        print(keyword, 'sougou search is success')

        for item in data:
            date = int(item['date'])
            value = item['pv']
            yield SougouKeyWordObject("sougou", int(value), date)

    def get_alibaba_keyword_buy_index(self, keyword: str, pur1688flag: bool = True, taobaoflag: bool = True,
                                      supplyflag: bool = True) -> dict:
        """

        获取淘宝，1688某商品用户采购总数量，返回一年的数据

        :return:
        :rtype:dict
        :param keyword:商品关键词
        :param pur1688flag:是否返回1688采购指数
        :param taobaoflag:是否返回淘宝采购指数
        :param supplyflag:是否返回1688供应指数
        :return:{"1688采购指数": pur1688 if pur1688flag else None, "淘宝采购指数": taobao if taobaoflag else None,
                "1688供应指数": supply1688 if supplyflag else None, "最近时间": lastdate,
                "最远时间": olddate}
        """

        url = 'http://index.1688.com/alizs/market.htm'
        query_string_parameters = {
            'keywords': keyword,
            'n': 'y',
            'categoryId': '',
        }
        response = requests.post(url=url, data=query_string_parameters)
        if response.status_code != 200:
            raise ConnectionError("网络请求"
                                  "出问题")
        soup = BeautifulSoup(response.text, 'lxml')
        result = soup.find(name='input', attrs={"id": "main-chart-val"})
        lastdate = soup.find(name="input", attrs={"id": "main-chart-lastDate"}).get("value")
        localtime = time.strptime(lastdate, "%Y-%m-%d")
        t = time.mktime(localtime) - 3600 * 24 * 365
        olddate = time.strftime("%Y-%m-%d", time.gmtime(t))  # 最远的时间
        data = json.loads(result.get("value"))

        pur1688: list = data['purchaseIndex1688']['index']['history']  # 1688采购指数
        taobao: list = data['purchaseIndexTb']['index']['history']  # 淘宝采购指数
        supply1688: list = data['supplyIndex']['index']['history']  # 1688供应指数
        return {"1688采购指数": pur1688 if pur1688flag else None, "淘宝采购指数": taobao if taobaoflag else None,
                "1688供应指数": supply1688 if supplyflag else None, "最近时间": lastdate,
                "最远时间": olddate}
