import requests
from urllib.parse import urlencode
from spyderpro.portconnect.internetconnect import Connect

"""股票模块"""
'''
该模块包括港股和泸深A股实时数据
'''


class Stock(Connect):

    def __init__(self, user_agent: str = None):
        """请求参数初始化
        :type user_agent: str
        :param:浏览器
        """

        self.request = requests.Session()

        self.headers = dict()

        if user_agent is None:
            self.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 ' \
                                         '(KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'

        else:
            self.headers['User-Agent'] = user_agent
        self.query_string_parameters = {
            'block': '',
            'commodityid': 0,
            'title': 15,
            'direction': 0,
            'start': '',
            'number': '',  # 一次返回对数据量，最大100，即两页
        }

    def get_real_time_a_stock(self, page: int, block: int = 2, number: int = 50) -> list:
        """获取泸深A股实时数据
        :rtype: iterable[dict]
        :param page: 第几页,范围为1-43
        :param block: 请求类型，默认2，暂且支持2
        :param number: 一次请求返回多少条数据，建议默认值50
        :return:iterable[{"代码": code, '名称': name, "最新价": price, '涨跌幅': updownrate, '昨收': lastclose, '今开': todayopen,
                   '最高': high, '最低': low, '成交量': volume, '成交额': priceweight, '换手': exchangeratio,
                   '振幅': vibration_ratio, '量比': volumeratio
                   },,,,,]
        """

        assert isinstance(page, int)
        if page < 1 or page > 43:
            raise TypeError("page参数有误")
        self.headers['Host'] = 'webstock.quote.hermes.hexun.com'
        pre_url = 'http://webstock.quote.hermes.hexun.com/a/sortlist?'
        parameters = self.query_string_parameters
        parameters['block'] = block
        parameters['number'] = number
        parameters['start'] = (page - 1) * 50
        parameters[
            'column'] = "code ,name,price,updownrate,LastClose,open,high,low,volume,priceweight,amount,exchangeratio," \
                        "VibrationRatio,VolumeRatio"

        url = pre_url + urlencode(parameters)
        par = "\((.*?)\);"
        g: dict = self.connect(par, url)

        for value in g['Data'][0]:
            code = value[0]  # 代码
            name = value[1]  # 名称
            price = float(value[2]) / 100  # 最新价
            updownrate = float(value[3]) / 100  # 涨跌幅
            lastclose = float(value[4]) / 100  # 昨收
            todayopen = float(value[5]) / 100  # 今开
            high = float(value[6]) / 100  # 最高
            low = float(value[7]) / 100  # 最低
            volume = float(value[8]) / 100  # 成交量
            priceweight = value[10]  # 成交额
            exchangeratio = float(value[11]) / 100  # 换手
            vibration_ratio = float(value[12]) / 100  # 振幅
            volumeratio = float(value[13]) / 100  # 量比

            yield {"代码": code, '名称': name, "最新价": price, '涨跌幅': updownrate, '昨收': lastclose, '今开': todayopen,
                   '最高': high, '最低': low, '成交量': volume, '成交额': priceweight, '换手': exchangeratio,
                   '振幅': vibration_ratio, '量比': volumeratio
                   }

    def get_real_time_gb_hk_stock(self, page: int, block: int = 259, number: int = 50) -> list:
        """获取泸深港股实时数据
        :rtype: iterable
        :param page:
        :param block:
        :param number:
        :return:iterable[{"代码": , '名称': , "最新价": , '涨跌幅': , '昨收': , '今开': ,
                            '最高': , '最低': , '成交额': ,
                            },,,,,,]
        """
        '''page::表示第几页数据，page范围为1-41
         返回迭代器字典数据：{"代码": , '名称': , "最新价": , '涨跌幅': , '昨收': , '今开': ,
                            '最高': , '最低': , '成交额': ,
                            }'''
        assert isinstance(page, int)
        if page < 1 or page > 41:
            raise TypeError("page参数有误")
        self.headers['Host'] = 'webhkstock.quote.hermes.hexun.com'
        pre_url = 'http://webhkstock.quote.hermes.hexun.com/gb/hk/sortlist?'
        parameters = self.query_string_parameters
        parameters['block'] = block
        parameters['start'] = (page - 1) * 50
        parameters['number'] = number
        url = pre_url + urlencode(
            parameters) + "&column=code,name,price,open,LastClose,updownrate,volume,high,low,priceweight"

        par = "\((.*?)\);"
        g: dict = self.connect(par, url)

        for value in g['Data'][0]:
            code = value[0]  # 代码
            name = str(value[1]).encode('utf-8').decode("utf-8")  # 名称
            price = float(value[2]) / 1000  # 最新价
            todayopen = float(value[3]) / 1000  # 开盘价
            lastclose = float(value[4]) / 1000  # 前收盘
            updownrate = float(value[5]) / 100  # 涨跌幅
            priceweight = float(value[6]) / 10000  # 成交量
            high = float(value[7]) / 1000  # 最高价
            low = float(value[8]) / 1000  # 最低价

            yield {"代码": code, '名称': name, "最新价": price, '涨跌幅': updownrate, '昨收': lastclose, '今开': todayopen,
                   '最高': high, '最低': low, '成交额': priceweight,
                   }
