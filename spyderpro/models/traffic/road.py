class RoadInfo:
    """
    道路基本交通信息
    """

    def __init__(self, road_name, road_dir, road_speed, road_id, cur_rate, coords):
        self.road_name = road_name
        self.road_dir = road_dir
        self.road_speed = road_speed
        self.road_id = road_id
        self.cur_rate = cur_rate
        self.coords = coords

    def __str__(self):
        return "道路名:{road_name},方向:{road_dir},速度:{road_speed},当前拥堵指数：{cur_rate},道路pid:{road_id}," \
               "道路经纬度：{coords}".format(road_name=self.road_name, road_dir=self.road_dir, road_speed=self.road_speed,
                                       cur_rate=self.cur_rate,
                                       road_id=self.road_id,
                                       coords=self.coords)


class RoadData:
    """
    一条道路拥有的具体数据--拥堵排名，时间，交通数据
    """

    def __init__(self, num: int, detailt_time_list: list, road_data_list: list):
        self.num: int = num
        self.detailt_time_list: list = detailt_time_list
        self.road_data_list: list = road_data_list

    def __str__(self):
        return "排名：{num}，时间：{ttime}，道路数据集：{data}".format(num=self.num, ttime=self.detailt_time_list,
                                                         data=self.road_data_list)


class Road:
    """
    道路类，用于记录该天的城市道路交通拥堵数据，实例属性有：region_id: 城市标识,roadname:道路名字, speed:速度,dircetion:方向,
    ,bounds:经纬度范围,data:拥堵数据集

    Attributes:
        region_id :INT 类型属性，用于记录城市标识
        roadname :String类型,用于记录道路名字
        speed : FLOAT类型,用于记录速度
        direction : String类型，用于记录方向
        bounds : Dict类型，用于记录经纬度范围，格式为{"coords": [{"lon": "120.324071", "lat": "31.633172"}，，，，]}
        data : Dict类型，用于记录拥堵数据集，格式为{"num": 0, "time": ["02:50", "02:55", ], "data": ["1.05", "1.06", ]}

    """
    __slots__ = ['region_id', 'roadname', 'speed', 'direction', 'bounds', 'data', "num", "rate"]

    def __init__(self, pid: int, roadname: str, speed: float, dircetion: str, bounds: dict, data: dict, num: int,
                 rate: float):
        """
        Args:
            pid: INT 类型属性，城市标识
            roadname:String类型,道路名字
            speed:FLOAT类型,速度
            dircetion:String类型，方向
            bounds:Dict类型，经纬度范围，格式为{"coords": [{"lon": "120.324071", "lat": "31.633172"}，，，，]}
            data: Dict类型，拥堵数据集，格式为{"num": 0, "time": ["02:50", "02:55", ], "data": ["1.05", "1.06", ]}
            num:INT类型，表示道路排在第几名
            rate:Float类型表示拥堵指数

        """
        self.region_id: int = pid
        self.roadname: str = roadname
        self.speed: float = speed
        self.direction: str = dircetion
        self.bounds: dict = bounds
        self.data: dict = data
        self.num: int = num
        self.rate: float = rate

    def __str__(self):
        return "标识:{0},路名：{1}，拥堵指数:{2},方向：{3}，速度：{4},道路经纬度：{5}".format(self.region_id, self.roadname, self.rate,
                                                                       self.direction,
                                                                       self.speed, self.bounds)
