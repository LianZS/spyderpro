class DayilTraffic:
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





class YearTraffic:
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
