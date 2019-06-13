FundModel.py模块

A.类Fund

1.get_real_time_fund(self, page: int, enddate: str = time.strftime('%Y-%m-%d', time.localtime())):获取开放式基金数据

        :param page: 第几页面
        :param enddate:哪天的数据
        :rtype: list[dict]
        :return:list[{"基金代码": , "基金简称": , "今天累计净值": , "今天基金净值": ,
                   "昨天累计净值": , "昨天基金净值": , "日涨跌": , "今年回报率": ,
                   "购买状态": , " 赎回状态": },,,,,]
        根据endate来确定请求某天数据，一般默认today，page来确定获取第几页的数据，请求成功时循环 yield dict数据，否则抛出ConnectionError

StockMarket.py模块

A.类Stock

1.get_real_time_a_stock(self, page: int, block: int = 2, number: int = 50):获取泸深A股实时数据

        
        :rtype: iterable[dict]
        :param page: 第几页,范围为1-43
        :param block: 请求类型，默认2，暂且支持2
        :param number: 一次请求返回多少条数据，建议默认值50
        :return:iterable[{"代码": code, '名称': name, "最新价": price, '涨跌幅': updownrate, '昨收': lastclose, '今开': todayopen,
                   '最高': high, '最低': low, '成交量': volume, '成交额': priceweight, '换手': exchangeratio,
                   '振幅': vibration_ratio, '量比': volumeratio
                   },,,,,]
        根据page来确定要获取那一页数据，block为请求类型，一般默认为2，number表示一次请求返回多少条数据，默认50条，请求成功时循环返回yield dict格式数据，
        否则抛出ConnectionError
2.get_real_time_gb_hk_stock(self, page: int, block: int = 259, number: int = 50):获取泸深港股实时数据

        :rtype: list
        :param page:
        :param block:
        :param number:
        :return:iterable[{"代码": , '名称': , "最新价": , '涨跌幅': , '昨收': , '今开': ,
                            '最高': , '最低': , '成交额': ,
                            },,,,,,]
                         
        根据page来确定要获取那一页数据，block为请求类型，一般默认为259，number表示一次请求返回多少条数据，默认50条，请求成功时循环返回yield dict格式数据，
        否则抛出ConnectionError
