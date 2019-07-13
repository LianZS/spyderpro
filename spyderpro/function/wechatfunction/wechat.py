

from spyderpro.models.InternetData.wechatpublic import WechatPublic


class Wechat:
    def get_all_public(self, start: int, end: int, seq: int = 1):
        """获取全网公众号到信息及文章链接
        链接：https://www.wxnmh.com/user-pid.htm
        :param start: 从第几个公众号开始
        :param end: 到第几个公众号结束
        :param seq: 间隔
        :return iterable([WechatPublic_Info（page:页数，name:"公众号",pid "微信号",articles：'文章列表'）,,,,,])
        """
        wechat = WechatPublic()
        for pid, url in wechat.product_url(start, end, seq):# 这里高并发还未解决
            result = wechat.reuqest_public(pid, url)
            for i in result:
                print(i)

Wechat().get_all_public(1,4)