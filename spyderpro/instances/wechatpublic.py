class WechatUrl:
    __slots__ = ['pid', 'url']

    def __init__(self, pid: int, url: str):
        self.pid = pid
        self.url = url
