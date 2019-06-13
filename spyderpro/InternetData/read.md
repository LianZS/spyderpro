Keyword.py模块

A.类KeyWord

1.get_keyword_search_index(self, keyword: str, baidu: bool = True, haosou: bool = True, sougou: bool = True,
                                 pc: bool = True, modile: bool = True):能够获取各大浏览器关键词搜索次数，返回30天的搜索数据
                                 
        :rtype: iterable
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
               
        请求成功时根据关键词来获取百度，360，好搜浏览器的搜索频率，并以list返回各类数据；否则抛出ConnectionError
        
2.get_alibaba_keyword_buy_index(self, keyword: str, pur1688flag: bool = True, taobaoflag: bool = True,
                                      supplyflag: bool = True):获取淘宝，1688某商品用户采购总数量，返回一年的数据
                                      
                                 
        :rtype:dict
        :param keyword:商品关键词
        :param pur1688flag:是否返回1688采购指数
        :param taobaoflag:是否返回淘宝采购指数
        :param supplyflag:是否返回1688供应指数
        :return:{"1688采购指数": pur1688 if pur1688flag else None, "淘宝采购指数": taobao if taobaoflag else None,
                "1688供应指数": supply1688 if supplyflag else None, "最近时间": lastdate,
                "最远时间": olddate}
                
        根据商品关键词来获取该商品在市场上的购买数据，返回dict格式的一年购买数据，否则抛出ConnectionError
        
        
MobileKeyword.py模块

A.类MobileKeyWord

1.get_mobile_type_rate(self, year: int, startmonth: int = None, endmonth: int = None):获取某个时段的中国境内各手机机型的占有率
      
        
        :rtype:iterable
        :param year:年份
        :param startmonth: 开始月份
        :param endmonth:结束月份
        :return :iterable[{"机型": value['k'], "占有率": value['r']},,,,,,]
        若startmonth为none，则自动获取最近时间的统计数据，若endmonth为none，则只请求一个月的数据。
2.get_mobile_brand_rate(self, year: int, startmonth: int = None, endmonth: int = None):获取某时段中国境内各手机品牌占用率
        
        
        :rtype: iterable
        :param year: 年份
        :param startmonth:开始月份
        :param endmonth: 结束月份
        :return :iterable[{"品牌": value['k'], "占有率": value['r']},,,,,,]
        若startmonth为none，则自动获取最近时间的统计数据，若endmonth为none，则只请求一个月的数据。
        
        
   
3.get_mobile_resolution_rate(self, year: int, startmonth: int = None, endmonth: int = None): 获取某时段中国境内各手机分辨率占用率

        
        :rtype: iterable
        :param year: 年份
        :param startmonth:开始月份
        :param endmonth: 结束月份
        :return :iterable[{"分辨率": value['k'], "占有率": value['r']},,,,,,]
        若startmonth为none，则自动获取最近时间的统计数据，若endmonth为none，则只请求一个月的数据。
        
4.get_mobile_system_rate(self, year: int, startmonth: int = None, endmonth: int = None):获取某时段中国境内各手机系统版本占用率
        
        :rtype: iterable
        :param year: 年份
        :param startmonth:开始月份
        :param endmonth: 结束月份
        :return :iterable[{"操作系统": value['k'], "占有率": value['r']},,,,,,]
        若startmonth为none，则自动获取最近时间的统计数据，若endmonth为none，则只请求一个月的数据。
5.get_mobile_operator_rate(self, year: int, startmonth: int = None, endmonth: int = None):获取某时段中国境内各手机运营商占用率
        
        
        :rtype: iterable
        :param year: 年份
        :param startmonth:开始月份
        :param endmonth: 结束月份      
        :return :iterable[{"运营商": value['k'], "占有率": value['r']},,,,,,]
        若startmonth为none，则自动获取最近时间的统计数据，若endmonth为none，则只请求一个月的数据。
        
        
6.get_mobile_network_rate(self, year: int, startmonth: int = None, endmonth: int = None):获取某时段中国境内各手机网络占用率
        
        :rtype: list
        :param year: 年份
        :param startmonth:开始月份
        :param endmonth: 结束月份
        :return :iterable[{"网络": value['k'], "占有率": value['r']},,,,,,]
        若startmonth为none，则自动获取最近时间的统计数据，若endmonth为none，则只请求一个月的数据。
        