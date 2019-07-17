from typing import List
from spyderpro.function.keywordfunction.parent import Parent

from spyderpro.models.InternetData.keyword import KeyWord, KeyWordObject


class SearchKeyword(Parent):

    def browser_keyword_frequency(self, keyword: str, baidu: bool = True, weixin=True,
                                  pc: bool = True, modile: bool = True) -> List[KeyWordObject]:
        """
        获取浏览器关键词搜索频率
        :param keyword:关键词
        :param baidu:是否使用百度引擎
        :param weixin:是否使用微信搜索

        :param pc:是否获取pc端数据
        :param modile:是否移动端水
        :return:[KeyWordObject,KeyWordObject]
        """
        browser = KeyWord()
        result = browser.get_keyword_search_index(keyword=keyword)
        return result.__next__()

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
