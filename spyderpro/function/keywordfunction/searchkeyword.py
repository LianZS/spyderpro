from typing import List
from spyderpro.function.keywordfunction.parent import Parent

from spyderpro.models.InternetData.keyword import KeyWord, BaiduKeyWordObject


class SearchKeyword(Parent):

    def baidu_browser_keyword_frequency(self, keyword: str, baidu: bool = True,
                                        pc: bool = True, modile: bool = True) -> BaiduKeyWordObject:
        """
        获取百度浏览器关键词搜索频率
        :param keyword:关键词
        :param baidu:是否使用百度引擎
        :param weixin:是否使用微信搜索

        :param pc:是否获取pc端数据
        :param modile:是否移动端水
        :return:[KeyWordObject,KeyWordObject]
        """
        browser = KeyWord()
        result = browser.baidu_get_keyword_search_index(keyword=keyword)

        try:
            return result
        except Exception:
            return None

    def wechat_browser_keyword_frequency(self, keword, startdate, enddate):
        browser = KeyWord()
        result = browser.wechat_get_keyword_search_index(keyword=keword, startDate=startdate, endDate=enddate)
        return result

    def sougou_browser_keyword_frequency(self, keword):
        browser = KeyWord()
        result = browser.sougou_get_keyword_search_index(keyword=keword)
        return result

    def alibaba_goods_purchased_frequency(self, keyword: str, pur1688flag: bool = True, taobaoflag: bool = True,
                                          supplyflag: bool = True) -> dict:
        # **************该功能目前有bug**************

        """
        获取淘宝，1688某商品用户采购总数量，返回一年的数据

        :param keyword:
        :param pur1688flag:
        :param taobaoflag:
        :param supplyflag:
        :return:
        """
        browser = KeyWord()
        result = browser.get_alibaba_keyword_buy_index(keyword=keyword)
        return result
