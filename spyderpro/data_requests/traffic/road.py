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

    def __init__(self, num: int, detailt_time_list, road_data_list, coords=None):
        self.num: int = num
        self.detailt_time_list = detailt_time_list
        self.road_data_list = road_data_list
        self.coords = coords  # 道路经纬度

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

    def __init__(self, pid: int, roadname: str, speed: float, dircetion: str, bounds: dict, road_index_data_list: list,
                 time_data_list: list, num: int, rate: float):
        """
        Args:
            pid: INT 类型属性，城市标识
            roadname:String类型,道路名字
            speed:FLOAT类型,速度
            dircetion:String类型，方向
            bounds:Dict类型，经纬度范围，格式为{"coords": [{"lon": "120.324071", "lat": "31.633172"}，，，，]}
            road_index_data_list: List，拥堵数据集，格式["1.05", "1.06", ]
            time_data_list:List，格式【"00"】
            num:INT类型，表示道路排在第几名
            rate:Float类型表示拥堵指数

        """
        self.region_id: int = pid
        self.roadname: str = roadname
        self.speed: float = speed
        self.direction: str = dircetion
        self.bounds: dict = bounds
        self.road_index_data_list: list = road_index_data_list
        self.time_data_list: list = time_data_list
        self.num: int = num
        self.rate: float = rate

    def __str__(self):
        return "标识:{pid},路名：{road_name}，拥堵指数:{cur_rate},方向：{dir}，速度：{speed},时间集合:{times}，拥堵数据集：" \
               "{indexs},道路经纬度：{coords}".format(pid=self.region_id, road_name=self.roadname,
                                                cur_rate=self.rate,
                                                dir=self.direction,
                                                speed=self.speed, indexs=self.road_index_data_list,
                                                times=self.time_data_list,
                                                coords=self.bounds)
