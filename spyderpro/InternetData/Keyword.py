import requests
import json
import time
from bs4 import BeautifulSoup
from spyderpro.Connect.InternetConnect import Connect


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

    def get_keyword_search_index(self, keyword: str, baidu: bool = True, haosou: bool = True, sougou: bool = True,
                                 pc: bool = True, modile: bool = True) :

        """
        能够获取浏览器的关键词搜索频率

        :rtype: list[dict]
        :param keyword:搜索关键词
        :param baidu: 是否返回百度相关搜索量
        :param haosou: 是否返回好搜相关搜索量
        :param sougou: 是否返回搜狗相关搜索量
        :param pc: 是否返回pc端相关搜索量
        :param modile: 是否返回移动端相关搜索量
        :return:iterable[{"百度最新统计时间": baidu_update, "PC端": baidu_pc, "移动端": baidu_mobile, "整体": baidu_all}
                   if baidu else None,
                   {"360最新统计时间": haosou_update, "PC端": haosou_pc, "移动端": haosou_mobile,
                    "整体": haosou_all}
                   if haosou else None,
                   {"搜狗最新统计时间": sougou_update, "PC端": sougou_pc, "移动端": sougou_mobile,
                    "整体": sougou_all}
                   if sougou else None]
        """

        url = "http://index.chinaz.com/index/" + keyword
        par = "eval\\((.*?)\\);"
        g: dict = self.connect(par, url)
        for baidu_value, haosou_value, sougou_value in zip(g['baidu'], g['haosou'], g['sogou']):
            baidu_update = baidu_value.get("update")  # 百度最近关键词收编时间
            baidu_all = baidu_value['all']['index']  # 百度30天内总的搜索次数
            baidu_pc = baidu_value['pc']['index'] if pc else None  # 百度电脑端搜索量
            baidu_mobile = baidu_value['mobile']['index'] if modile else None  # 百度手机端搜索量
            haosou_update = haosou_value.get("update")  # 360最近关键词收编时间
            haosou_all = haosou_value['all']['index']  # 360 30天内总的搜索次数
            haosou_pc = haosou_value['pc']['index'] if pc else None  # 360 电脑端搜索量
            haosou_mobile = haosou_value['mobile']['index'] if modile else None  # 360手机端搜索量
            sougou_update = sougou_value.get("update")  # 搜狗最近关键词收编时间
            sougou_all = sougou_value['all']['index']  # 搜狗30天内总的搜索次数
            sougou_pc = sougou_value['pc']['index'] if pc else None  # 搜狗电脑端搜索量
            sougou_mobile = sougou_value['mobile']['index'] if modile else None  # 搜狗手机端搜索量
            yield [{"百度最新统计时间": baidu_update, "PC端": baidu_pc, "移动端": baidu_mobile, "整体": baidu_all}
                   if baidu else None,
                   {"360最新统计时间": haosou_update, "PC端": haosou_pc, "移动端": haosou_mobile,
                    "整体": haosou_all}
                   if haosou else None,
                   {"搜狗最新统计时间": sougou_update, "PC端": sougou_pc, "移动端": sougou_mobile,
                    "整体": sougou_all}
                   if sougou else None]

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


# d = KeyWord().get_alibaba_keyword_buy_index("数据线")
# print(d)
