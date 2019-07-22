class TrafficClass:
    """
    城市实时交通拥堵类，用于记录该天的城市的交通拥堵数据，类实例属性有region_id：城市标识, date:日期，index：指数,
    detailtime：时间


    Attributes:

        region_id:INT 类型属性，用于记录城市标识
        date:INT 类型属性,用于记录当前的日期，格式为yyyymmdd
        index: FLOAT类型，用于记录该时间点的拥堵指数
        detailtime: String类型,用于记录详细时间，格式为HH：MM：SS
    """
    __slots__ = ['region_id', 'date', 'index', 'detailtime']

    def __init__(self, pid: int, ddate: int, iindex: float, detailtime):
        """
        Args:

            pid: INT 类型属性，城市标识
            ddate:INT 类型属性,当前的日期，格式为yyyymmdd
            iindex: FLOAT类型，该时间点的拥堵指数
            detailtime:String类型,详细时间，格式为HH：MM：SS
        """
        self.region_id: int = pid
        self.date: int = ddate
        self.index: float = iindex
        self.detailtime: str = detailtime

    def __str__(self):
        return "日期：{0}，时间：{1}，指数{2},标识{3}".format(self.date, self.detailtime, self.index, self.region_id)


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
    __slots__ = ['region_id', 'roadname', 'speed', 'direction', 'bounds', 'data']

    def __init__(self, pid: int, roadname: str, speed: float, dircetion: str, bounds: dict, data: dict):
        """
        Args:
            pid: INT 类型属性，城市标识
            roadname:String类型,道路名字
            speed:FLOAT类型,速度
            dircetion:String类型，方向
            bounds:Dict类型，经纬度范围，格式为{"coords": [{"lon": "120.324071", "lat": "31.633172"}，，，，]}
            data: Dict类型，拥堵数据集，格式为{"num": 0, "time": ["02:50", "02:55", ], "data": ["1.05", "1.06", ]}

        """
        self.region_id: int = pid
        self.roadname: str = roadname
        self.speed: float = speed
        self.direction: str = dircetion
        self.bounds: dict = bounds
        self.data: dict = data

    def __str__(self):
        return "标识{0},路名：{1}，方向：{2}，速度：{3}，经纬度；{4}，指数集：{5}".format(self.region_id, self.roadname, self.direction,
                                                                   self.speed, self.bounds,
                                                                   self.data)


class Year:
    """
    城市交通季度类，用于记录该天的城市的季度交通拥堵数据，类实例属性有region_id：城市季度标识, date：日期,index：拥堵指数

       Attributes:


           region_id：INT 类型属性，用于记录城市季度标识
           date: INT 类型属性,用于记录当前的日期，格式为yyyymmdd
           index: FLOAT类型，用于记录该时间点的拥堵指数


    """

    __slots__ = ['region_id', 'date', 'index']

    def __init__(self, pid, date: int, index: float):
        """
        Args:
            pid:INT 类型属性，城市季度标识
            date:INT 类型属性,当前的日期，格式为yyyymmdd
            index  FLOAT类型，该时间点的拥堵指数

        """
        self.region_id: int = pid
        self.date: int = date
        self.index: float = index
