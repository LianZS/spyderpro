from threading import Thread, Event
from queue import Queue

from spyderpro.models.InternetData.wechatpublic import WechatPublic


class Wechat:
    wechat = WechatPublic()

    def get_all_public(self, start: int, end: int, seq: int = 1):
        """获取全网公众号到信息及文章链接
        链接：https://www.wxnmh.com/user-pid.htm
        :param start: 从第几个公众号开始
        :param end: 到第几个公众号结束
        :param seq: 间隔
        :return iterable([WechatPublic_Info（page:页数，name:"公众号",pid "微信号",articles：'文章列表'）,,,,,])
        """
        Thread(target=self.wait_for_data, args=()).start()
        Thread(target=self.wait_for_data, args=()).start()

        for pid, url in self.wechat.product_url(start, end, seq):  # 这里高并发还未解决
            result = self.wechat.reuqest_public(pid, url)  # 对断网处理存在漏洞

    def wait_for_data(self):
        while 1:

            try:
                data = self.wechat.q.get(timeout=3)  # 当3秒依旧未收到信息后，说明任务已经结束了，此时退出
            except Exception:
                break


Wechat().get_all_public(1, 8)
