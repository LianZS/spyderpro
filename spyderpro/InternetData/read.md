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
        若startmonth为none，则自动获取最近时间的统计数据，若endmonth为none，则只请求一个月的数据。若网络失败，抛出ConnectionError

2.get_mobile_brand_rate(self, year: int, startmonth: int = None, endmonth: int = None):获取某时段中国境内各手机品牌占用率
        
        
        :rtype: iterable
        :param year: 年份
        :param startmonth:开始月份
        :param endmonth: 结束月份
        :return :iterable[{"品牌": value['k'], "占有率": value['r']},,,,,,]
        若startmonth为none，则自动获取最近时间的统计数据，若endmonth为none，则只请求一个月的数据。若网络失败，抛出ConnectionError
        
        
   
3.get_mobile_resolution_rate(self, year: int, startmonth: int = None, endmonth: int = None): 获取某时段中国境内各手机分辨率占用率

        
        :rtype: iterable
        :param year: 年份
        :param startmonth:开始月份
        :param endmonth: 结束月份
        :return :iterable[{"分辨率": value['k'], "占有率": value['r']},,,,,,]
        若startmonth为none，则自动获取最近时间的统计数据，若endmonth为none，则只请求一个月的数据。若网络失败，抛出ConnectionError
        
4.get_mobile_system_rate(self, year: int, startmonth: int = None, endmonth: int = None):获取某时段中国境内各手机系统版本占用率
        
        :rtype: iterable
        :param year: 年份
        :param startmonth:开始月份
        :param endmonth: 结束月份
        :return :iterable[{"操作系统": value['k'], "占有率": value['r']},,,,,,]
        若startmonth为none，则自动获取最近时间的统计数据，若endmonth为none，则只请求一个月的数据。若网络失败，抛出ConnectionError
5.get_mobile_operator_rate(self, year: int, startmonth: int = None, endmonth: int = None):获取某时段中国境内各手机运营商占用率
        
        
        :rtype: iterable
        :param year: 年份
        :param startmonth:开始月份
        :param endmonth: 结束月份      
        :return :iterable[{"运营商": value['k'], "占有率": value['r']},,,,,,]
        若startmonth为none，则自动获取最近时间的统计数据，若endmonth为none，则只请求一个月的数据。若网络失败，抛出ConnectionError
        
        
6.get_mobile_network_rate(self, year: int, startmonth: int = None, endmonth: int = None):获取某时段中国境内各手机网络占用率
        
        :rtype: list
        :param year: 年份
        :param startmonth:开始月份
        :param endmonth: 结束月份
        :return :iterable[{"网络": value['k'], "占有率": value['r']},,,,,,]
        若startmonth为none，则自动获取最近时间的统计数据，若endmonth为none，则只请求一个月的数据。若网络失败，抛出ConnectionError


Userhabit.py模块

A.类UserHabit

1.get_user_portrait(self, year: int, startmonth: int = None, endmonth: int = None):
获取用户图像---性别分布 ，年龄分布，消费偏好，区域热度，应用偏好

        :param year:年份
        :param startmonth:开始月份
        :param endmonth:结束月份
        :rtype: iterable 
        :return iterable[{"区域热度 ": name, "占比": share}]     
        若startmonth为none，则自动获取最近时间的统计数据，若endmonth为none，则只请求一个月的数据。若网络失败，抛出ConnectionError


2. get_user_behavior(self, year: int, endmonth: int = None): 获取用户行为---人均安装应用趋势，人均启动应用趋势
       
       

        :param year:年份
        :param startmonth:开始月份
        :param endmonth:结束月份
        :rtype: iterable
        :return iterable[{"日期": date, "人均安装应用": install, "人均启动应用": active}] 
        若startmonth为none，则自动获取最近时间的统计数据，若endmonth为none，则只请求一个月的数据。若网络失败，抛出ConnectionError


WechatPublic.py模块

A.类WechatPublic

1.get_all_public(self, start: int, end: int, seq: int = 1):  获取全网公众号到信息及文章链接
        链接：https://www.wxnmh.com/user-pid.htm
        
        :param start: 从第几个公众号开始
        :param end: 到第几个公众号结束
        :param seq: 间隔
        :return iterable[{'信息':{"公众号": name, "微信号": public_pid},'文章列表':datalist},,,,,]
        start最小为1，公众号标示以数字为区别，seq默认取1。若网络失败，抛出ConnectionError
      
2.reuqest_public(self, pid: int, url: str) : 请求公众号数据借口

        :param pid:公众号数字id
        :param url: 首页链接
        :return  dict
        若网络失败，抛出ConnectionError
        
3.get_detail_public_info(self, pid: int, url: str) :获取文章标题和链接

        :param pid:公众号数字id
        :param url: 首页链接
        :return  {'信息':{"公众号": name, "微信号": public_pid},'文章列表':datalist}
        若网络失败，抛出ConnectionError
        
4.get_all_article(self, url):请求并处理文章列表
        
        :param url: 文章列表链接
        :return list[dict->{"标题": title, "链接": href}]
        若网络失败，抛出ConnectionError
        
5.search_public(self, public_pid: str):在微小宝搜索公众号

        :param public_pid:公众号账号
        :return {"总概况":,"历史数据":,}
        若网络失败，抛出ConnectionError
        
6.request_public_data(self, driver, url): 获取该公众号的详细数据：平均阅读量，最高阅读量，平均点赞，最高点赞等

        :param driver:实例
        :param url:链接
        :return   {"总概况":{"头条平均阅读量": average_read, "最高阅读量": hight_read, "头条平均点赞数": average_like,
                               "最高点赞数": hight_like},"历史数据":[{"日期": day, "总阅读数": read_num_total, "总点赞数": top_like_num_total, "发表文章数":
                articles_total}]}
        若网络失败，抛出ConnectionError
        
7.get_public_keyword(self, pid):获取关键词列表
        
        :param pid ：公众号id
        :return list[关键词]    
        若网络失败，抛出ConnectionError    
 