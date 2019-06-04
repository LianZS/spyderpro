import requests
import json
from bs4 import BeautifulSoup
from spyderpro.Connect.InternetConnect import Connect


class KeyWord(Connect):
    def __init__(self, user_agent: str = None):
        """请求参数初始化"""
        # user_agent：浏览器
        self.request = requests.Session()

        self.headers = dict()

        if user_agent is None:
            self.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 ' \
                                         '(KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'

        else:
            self.headers['User-Agent'] = user_agent

    def get_keyword_search_index(self, keyword: str):
        url = "http://index.chinaz.com/index/" + keyword
        par = "eval\((.*?)\);"
        g: dict = self.connect(par, url)
        for baidu_value, haosou_value, sougou_value in zip(g['baidu'], g['haosou'], g['sogou']):
            baidu_update = baidu_value.get("update")  # 百度最近关键词收编时间
            baidu_all = baidu_value['all']['index']  # 百度30天内总的搜索次数
            baidu_pc = baidu_value['pc']['index']  # 百度电脑端搜索量
            baidu_mobile = baidu_value['mobile']['index']  # 百度手机端搜索量
            haosou_update = haosou_value.get("update")  # 360最近关键词收编时间
            haosou_all = haosou_value['all']['index']  # 360 30天内总的搜索次数
            haosou_pc = haosou_value['pc']['index']  # 360 电脑端搜索量
            haosou_mobile = haosou_value['mobile']['index']  # 360手机端搜索量
            sougou_update = sougou_value.get("update")  # 搜狗最近关键词收编时间
            sougou_all = sougou_value['all']['index']  # 搜狗30天内总的搜索次数
            sougou_pc = sougou_value['pc']['index']  # 搜狗电脑端搜索量
            sougou_mobile = sougou_value['mobile']['index']  # 搜狗手机端搜索量

    def get_alibaba_keyword_buy_index(self, keyword):
        url = 'http://index.1688.com/alizs/market.htm'
        post = {
            'keywords': keyword,
            'n': 'y',
            'categoryId': '',
        }
        data = requests.post(url=url, data=post)
        soup = BeautifulSoup(data.text, 'lxml')
        result = soup.find(name='input', attrs={"id": "main-chart-val"})
        data = json.loads(result.get("value"))

        pur1688 = data['purchaseIndex1688']['index']['history']  # 1688采购指数
        taobao = data['purchaseIndexTb']['index']['history']  # 淘宝采购指数
        supply1688 = data['supplyIndex']['index']['history']  # 1688供应指数



KeyWord().get_alibaba_keyword_buy_index("数据线")
