import requests
import re
from bs4 import BeautifulSoup
from spyderpro.Connect.InternetConnect import Connect


class WechatPublic(Connect):
    def __init__(self, user_agent=None):
        """

        :type user_agent: str
        :param:user_agent：浏览器
        """

        self.request = requests.Session()

        self.headers = dict()

        if user_agent is None:
            self.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 ' \
                                         '(KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'

        else:
            self.headers['User-Agent'] = user_agent

    def get_all_public(self, start: int, end: int, seq: int = 1):
        """获取全网公众号到信息及文章链接
        链接：https://www.wxnmh.com/user-pid.htm
        :param start: 从第几个公众号开始
        :param end: 到第几个公众号结束
        :param seq: 间隔
        :return list[dict->{"标题": title, "链接": href}]
        """
        for pid in range(start, end, seq):
            url = 'https://www.wxnmh.com/user-{0}.htm'
            url = url.format(pid)
            self.reuqest_public(pid, url)

    def reuqest_public(self, pid: int, url: str):
        """
        请求公众号
        :param pid:公众号数字id
        :param url: 首页链接
        """
        result = self.get_detail_public_info(pid, url)
        for item in result:
            print(item)

    def get_detail_public_info(self, pid: int, url: str) -> list:
        """
        获取文章标题和链接
        :param pid:公众号数字id
        :param url: 首页链接
        :return  list[dict->{"标题": title, "链接": href}]
        """
        response = self.request.get(url=url, headers=self.headers)
        soup = BeautifulSoup(response.text, "lxml")
        keyword = soup.find(name="meta", attrs={"name": "keywords"}).get("content")
        info = keyword.split(",")
        name, public_pid = info[0], info[1]  # 公众号名字和微信号
        yield {"公众号": name, "微信号": public_pid}
        nav = soup.find(name="a", attrs={"class": "nav-link active"}).text
        articles_total_num = int(re.search("(\\d+)", nav, re.S).group(1))  # 总文章数
        pages = int(articles_total_num / 10.0 - 0.5)  # 文章总页数
        ''' #文章列表链接：https://www.wxnmh.com/user-pid-第几页文章.htm'''
        articles = soup.find_all(name="a", attrs={"target": "_blank", "href": re.compile(r"thread")})
        for value in articles:
            href = value.get("href")
            title = value.text
            yield {"标题": title, "链接": href}

        for page in range(2, pages):
            url = 'https://www.wxnmh.com/user-{0}-{1}.htm'.format(pid, page)
            result = self.get_all_article(url)

            for item in result:
                yield item

    def get_all_article(self, url) -> list:
        """
        请求并处理文章列表
        :param url: 文章列表链接
        :return list[dict->{"标题": title, "链接": href}]
        """
        response = self.request.get(url=url, headers=self.headers)

        soup = BeautifulSoup(response.text, "lxml")

        articles = soup.find_all(name="a", attrs={"target": "_blank", "href": re.compile(r"thread")})
        for value in articles:
            href = value.get("href")
            title = value.text
            yield {"标题": title, "链接": href}


WechatPublic().get_all_public(2, 10)
