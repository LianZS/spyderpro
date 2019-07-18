class TrafficClass:
    __slots__ = ['date', 'index', 'detailtime']

    def __init__(self, ddate, iindex, detailtime):
        self.date: int = ddate
        self.index: float = iindex
        self.detailtime: str = detailtime
