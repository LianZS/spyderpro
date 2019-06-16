from spyderpro.Connect.MysqlConnect import MysqlOperation


class Search_KeyWord(MysqlOperation):
    def __init__(self):
        pass

    def browser_keyword_frequency(self, keyword: str, baidu: bool = True, haosou: bool = True, sougou: bool = True,
                                  pc: bool = True, modile: bool = True):
        """
        获取3大浏览器关键词搜索频率
        :param keyword:
        :param baidu:
        :param haosou:
        :param sougou:
        :param pc:
        :param modile:
        :return:
        """
        pass

    def alibaba_goods_purchased_frequency(self, keyword: str, pur1688flag: bool = True, taobaoflag: bool = True,
                                          supplyflag: bool = True):
        """
        获取淘宝，1688某商品用户采购总数量，返回一年的数据

        :param keyword:
        :param pur1688flag:
        :param taobaoflag:
        :param supplyflag:
        :return:
        """
        pass

    def type_check(self, param, param_type):
        assert isinstance(param, param_type), "the type of param is wrong"
