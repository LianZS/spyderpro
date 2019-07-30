import requests
import re
import json
import csv
import os
import time
from threading import Thread, Semaphore
from queue import Queue
from selenium import webdriver
from typing import Iterator
from bs4 import BeautifulSoup
from urllib.parse import urlencode
from spyderpro.portconnect.internetconnect import Connect
from spyderpro.instances.wechat import WechatPublic_Info, ArticleInfo, WechatSituation, ArticleKeyWord
from spyderpro.instances.wechatpublic import WechatUrl


class WechatPublic(Connect):
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
        # self.errorqueue = Queue(5)  # 错误处理队列
        self.semaphore = Semaphore(10)  # 任务信号量
        self.dataqueue = Queue(20)  # 数据队列
        # self.wait = Semaphore(1)  # 每次只允许1个公众号运行

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

    def get_public_info(self, pid: int, url: str):

        """
        获取公众号名字和微信号
        :param pid:
        :param url:
        :return:
        """
        response = None
        try:
            response = self.request.get(url=url, headers=self.headers)
        except Exception:
            print("coonect error")
            self.dataqueue.put(1)
            return None
            # self.errorqueue.put(1)
        # if not self.errorqueue.empty():  # 任务恢复正常
        #     while self.errorqueue.qsize():
        #         self.errorqueue.get()

        soup = BeautifulSoup(response.text, "lxml")
        keyword = soup.find(name="meta", attrs={"name": "keywords"}).get("content")
        info: list = keyword.split(",")
        name, public_pid = info[0], info[1]  # 公众号名字和微信号
        self.dataqueue.put(self.WechatInfo(pid, name, public_pid))

    # def reuqest_public(self, pid: int, url: str) -> WechatPublic_Info:
    #     """
    #     请求公众号数据接口
    #     :param pid:公众号数字id
    #     :param url: 首页链接
    #     :return  dict
    # 
    #     """
    #     self.wait.acquire()
    #     result: WechatPublic_Info = self.get_detail_public_info(pid, url)
    #     return result

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

    """
    search_public--->request_public_data
    """

    def search_public(self, public_pid: str):
        """在微小宝搜索公众号详细信息入口pid的信息
        :param public_pid:公众号账号
        :return dict->{"pid": pid}
        """

        driver = self.chrome()
        driver.get("https://data.wxb.com/")
        element = driver.find_element_by_class_name("ant-input")
        element.send_keys(public_pid)
        driver.find_element_by_class_name("ant-btn-icon-only").click()
        # driver.get("https://data.wxb.com/searchResult?" + urlencode(query_string_parameters))
        response = driver.page_source
        driver.close()
        soup = BeautifulSoup(response, 'lxml')
        href = soup.find(name='a', attrs={"href": re.compile("/details/postRead?")}).get('href')  # 获取链接
        pid = re.search("id=(.*)", href, re.I).group(1)
        info = {"pid": pid}
        return info

    def request_public_data(self, pid) -> WechatSituation:

        """获取该公众号的详细数据：平均阅读量，最高阅读量，平均点赞，最高点赞等
        :return   WechatSituation("头条平均阅读量": average_read, "最高阅读量": hight_read, "头条平均点赞数": average_like,
                               "最高点赞数": hight_like,"发文数":count_article,"fans_num":粉丝数，"历史数据":data)

        """

        url = "https://data.wxb.com/account/stat/" + pid
        response = self.request.get(url=url, headers=self.headers).text
        g = json.loads(response)
        data = g['data']
        count_article_latest = data['count_article_latest_30']  # 发文次数

        fans_num_estimate = data['fans_num_estimate']  # 预估粉丝数

        max_read_latest = data['max_read_latest_30']  # 最高阅读数

        max_like_latest = data['max_like_latest_30']  # 最高在看数

        avg_read_num = data['avg_read_num_idx1']  # 头条平均阅读数

        avg_like_num = data['avg_like_num_idx1']  # 头条平均在看数

        datalist = self.request_history_data(pid)
        situation = WechatSituation(average_read=avg_read_num, hight_read=max_read_latest, average_like=avg_like_num,
                                    hight_like=max_like_latest, count_article=count_article_latest,
                                    fans_num=fans_num_estimate,
                                    data=datalist)

        return situation

    def request_history_data(self, pid) -> list:
        """
        获取公众号文章相关历史数据，比如阅读量等
        :param pid:
        :return:list[ArticleInfo]
        """
        query_string_parameters = {
            'period': '30',
            'start_date': '',
            'end_date': '',
            'is_new': '1'
        }
        url = "https://data.wxb.com/account/statChart/" + pid + "?" + urlencode(query_string_parameters)
        response = self.request.get(url=url, headers=self.headers)
        g = json.loads(response.text)
        data = g['data']
        datalist = list()
        for key in g['data'].keys():
            value = data[key]
            read_num_total = value['read_num_total']  # 总阅读量
            like_num_total = value['like_num_total']  # 在看量
            date = key
            arcitleinfo = ArticleInfo(read_num_total=read_num_total, like_num_total=like_num_total, date=date)

            datalist.append(arcitleinfo)
        return datalist

    def request_public_keyword(self, pid) -> list:
        """获取关键词列表
        :param pid ：公众号id
        :return list[ArticleKeyWord}
        """
        url = "https://data.wxb.com/account/content/" + pid
        response = self.request.get(url=url, headers=self.headers)
        g = json.loads(response.text)
        data = g['data']['article_keywords']
        datalist = list()
        for item in data:
            keyword = item['name']
            value = item['value']
            ak = ArticleKeyWord(keyword=keyword, value=value)
            datalist.append(ak)
        return datalist

    @staticmethod
    def chrome():
        option = webdriver.ChromeOptions()
        option.add_argument('headless')
        driver = webdriver.Chrome(chrome_options=option)
        return driver

    def get_detail_info(self, name):
        # rootpath = os.path.dirname(os.path.abspath(os.path.pardir))
        # print(rootpath)
        # exit()
        # filepath = os.path.join(rootpath,'datafile/wechatpublic.csv')
        rootpath = os.path.dirname(os.path.abspath(os.path.pardir))

        f = open(os.path.join(rootpath, name), 'a+', newline='')
        w = csv.writer(f)
        w.writerow(['标识', '公众号名', "公众号id"])
        while 1:
            wechatinfo = self.dataqueue.get()
            w.writerow([wechatinfo.pid, wechatinfo.name, wechatinfo.cards])
            f.flush()
