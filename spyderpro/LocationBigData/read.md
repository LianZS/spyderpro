PeopleFlow.py模块

A.类ScencePeopleFlow

1.peopleflow_info(self, peoplepid, historytype: int = 1):获取景区客流量
        
        :param peoplepid: 景区id
        :param historytype: 1表示现在的数据，2表示昨日数据，3表示最近的节假日数据
        :return: Generator[Dict[时刻, 客流量], Any, None]
        若网络失败，抛出ConnectionError

PeopleNum.py模块

A.类PeoplePositionin

1. get_PeoplePositionin_data(self, rank: int, max_num=4) :获取全国定位数据
    
    
        :param rank: 第几块数据文件
        :param max_num: 把数据文件分割成几块
        :return iterable[dict,,,,,]
        注意，返回的第一个元素是搜索时间  {"搜索时间": realtime}
        
C.PlacePeople.py模块

A.类PlaceTrend

1.get_allprovince(self) :获取所有省份
        
        :return: list[{"province":,},,]
2.get_alllcity(self, province: str) :获取省份下所有城市
        
        :param province: 省份名
        :return: list[{"省份": , "城市":}，，]
        
3.get_regions_bycity(self, province: str, city: str) :获取城市下所有景点信息


        :type province: str
        :type city:str
        :param province:省份
        :param city:城市
        :return  iterable[{"景点": , "id": },,,,]
        
4.getlocations(self, region_name: str, pid: int):获取景区流量趋势

        :param region_name: 景区
        :param pid: 景区id
        :return  iterable[{"景点": region_name, "日期": date, "数据": g[date]},,,,,]