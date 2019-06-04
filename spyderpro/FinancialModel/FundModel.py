import requests
import time
import json
import re
from urllib.parse import urlencode
from spyderpro.Connect.InternetConnect import Connect


class Fund(Connect):

    def __init__(self, user_agent: str = None):
        self.request = requests.Session()

        self.headers = dict()

        if user_agent is None:
            self.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 ' \
                                         '(KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'

        else:
            self.headers['User-Agent'] = user_agent
        self.query_string_parameters = {
            'enddate': '',
            'curpage': '',
            'pagesize': 20,
            'sortName': 'dayPrice',
            'sortType': 'down'

        }

    def get_real_time_fund(self, page: int, enddate: str = time.strftime('%Y-%m-%d', time.localtime())):
        """开放式基金实时数据"""
        '''
        yield {"基金代码": , "基金简称": , "今天累计净值": , "今天基金净值": ,
                   "昨天累计净值": , "昨天基金净值": , "日涨跌": , "今年回报率": ,
                   "购买状态": , " 赎回状态": }

        '''
        pre_url = 'http://jingzhi.funds.hexun.com/jz/JsonData/KaifangJingz.aspx?'
        parameters = self.query_string_parameters
        parameters['enddate'] = enddate
        parameters['curpage'] = page
        url = pre_url + urlencode(parameters)
        par = "callback\((.*?)\)"
        g: dict = self.connect(par, url)
        today = g['today']  # 今天
        daybefore = g["dayBefore"]  # 昨天
        cxlevelday = g['cxLevelday']  # 晨星三年评级时间
        data: list = g['list']
        for value in data:
            bamass = float(value['bAmass'])  # 昨天累计净值
            bnet = float(value['bNet'])  # 昨天基金净值
            buy_status = value['buyStatus']  # 购买状态
            redeem_status = value['redeemStatus']  # 赎回状态
            dayprice = value['dayPrice']  # 日涨跌
            fundcode = value['fundCode']  # 基金代码
            fundname = value['fundName']  # 基金简称
            tamass = float(value['tAmass'])  # 今天累计净值
            tnet = float(value['tNet'])  # 今天基金净值
            thisyear = value['thisyear']  # 今年回报率
            yield {"基金代码": fundcode, "基金简称": fundname, "今天累计净值": tamass, "今天基金净值": tnet,
                   "昨天累计净值": bamass, "昨天基金净值": bnet, "日涨跌": dayprice, "今年回报率": thisyear,
                   "购买状态": buy_status, " 赎回状态": redeem_status}
