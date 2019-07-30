import requests
import re
import csv
import os
import time
from threading import Thread, Semaphore
from queue import Queue
from typing import Iterator
from bs4 import BeautifulSoup
class WechatUrl:
    __slots__ = ['pid', 'url']

    def __init__(self, pid: int, url: str):
        self.pid = pid
        self.url = url

class WechatPublic_Info:
    """
    name:公众号
    pid:微信号
    articles:文章列表
    """
    __slots__ = ['page', 'name', 'public_pid', 'pid', 'articles']

    def __init__(self, page, name, public_pid, pid, articlelist):
        self.page = page
        self.name = name
        self.public_pid = public_pid
        self.pid = pid
        self.articles = articlelist

    def __str__(self):
        return "公众号:{0},标识：{1},第{2}页，微信号:{3},文章列表:{4}".format(self.public_pid, self.pid, self.page, self.name,
                                                              list(self.articles))


class WechatPublic:
    class WechatInfo:
        __slots__ = ['pid', 'name', 'cards']

        def __init__(self, pid, name, card):
            self.pid = pid
            self.name = name
            self.cards = card

    def __init__(self, user_agent=None):
        """

        :type user_agent: str
        :param:user_agent：浏览器
        """

        self.request = requests.Session()
        self.headers = dict()
        self.semaphore = Semaphore(10)  # 任务信号量
        self.dataqueue = Queue(20)  # 数据队列
        self.wait = Semaphore(1)

        if user_agent is None:
            self.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 ' \
                                         '(KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'

        else:
            self.headers['User-Agent'] = user_agent

    def product_url(self, start: int, end: int, seq: int = 1) -> Iterator[WechatUrl]:

        """
        产生请求链接
        :param start:
        :param end:
        :param seq:
        :return:
        """
        if end > 153362:
            raise AttributeError("end参数超过范围")
        for pid in range(start, end, seq):
            url = 'https://www.wxnmh.com/user-{0}.htm'
            url = url.format(pid)
            yield WechatUrl(pid=pid, url=url)

    def get_detail_public_info(self, pid: int, url: str):

        """
        获取文章标题和链接
        :param pid:公众号数字id
        :param url: 首页链接
        """
        response = None
        soup = None
        try:
            response = self.request.get(url=url, headers=self.headers)
            soup = BeautifulSoup(response.text, "lxml")

        except Exception:
            print("coonect error")
            self.dataqueue.put(1)
            time.sleep(3)
            return None

        keyword = soup.find(name="meta", attrs={"name": "keywords"}).get("content")
        info: list = keyword.split(",")
        name, public_pid = info[0], info[1]  # 公众号名字和微信号

        nav = soup.find(name="a", attrs={"class": "nav-link active"}).text
        articles_total_num = int(re.search("(\\d+)", nav, re.S).group(1))  # 总文章数
        pages = int(articles_total_num / 10.0 + 1)  # 文章总页数
        ''' #文章列表链接：https://www.wxnmh.com/user-pid-第几页文章.htm'''
        task_count = pages  # 判断该任务是否完成，若为0，则完成

        articles = soup.find_all(name="a", attrs={"target": "_blank", "href": re.compile(r"thread")})  # 该页所有文章
        datalist = list()

        '''第一页'''
        for value in articles:
            href = value.get("href")  # 链接
            title = value.text  # 标题
            datalist.append({"title": title, "href": href})

        wechatinfo = WechatPublic_Info(page=1, name=name, public_pid=public_pid, pid=pid, articlelist=iter(datalist))
        if len(datalist) == 0:
            self.dataqueue.put(1)

            return None
        self.dataqueue.put(wechatinfo)
        task_count -= 1  # 任务量减一
        ''''第2页开始'''

        def requests_next(nextpage, pid):

            nonlocal task_count
            datalist = []

            url = 'https://www.wxnmh.com/user-{0}-{1}.htm'.format(pid, nextpage)
            result = self.get_all_article(url)
            for item in result:
                datalist.append(item)

            if len(datalist) > 0:
                wechatinfo = WechatPublic_Info(page=nextpage, name=name, public_pid=public_pid, pid=pid,
                                               articlelist=iter(
                                                   datalist))
                # print(wechatinfo)
                self.dataqueue.put(wechatinfo)
            task_count -= 1  # 任务量减一

            self.semaphore.release()
        for page in range(2, pages + 1):
            self.semaphore.acquire()
            Thread(target=requests_next, args=(page, pid,)).start()
        while task_count:  # f当任务量为0时通知线程可以退出了
            continue
        self.dataqueue.put(1)  # 通知可以释放线程了

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

            yield {"title": title, "href": href}


def get_aritles(file):
    w = csv.writer(file)
    while 1:

        info = wechat.dataqueue.get()

        if info == 1:  # 1表示该公众号挖掘结束
            lock.release()
            break

        w.writerow(list(info.articles))

    file.close()


wechat = WechatPublic()

rootpath = os.path.dirname(os.path.abspath(os.path.curdir))
lock = Semaphore(1)
try:
    os.mkdir(os.path.abspath(os.path.join(rootpath, "wechat")))
except Exception:
    pass
for item in wechat.product_url(3, 153362):
    lock.acquire()
    print(item.url)
    f = open(os.path.join(rootpath, "wechat/" + str(item.pid) + '.csv'), 'a+', newline='')

    Thread(target=get_aritles, args=(f,)).start()

    Thread(target=wechat.get_detail_public_info, args=(item.pid, item.url,)).start()
