import requests
import re
import json
from selenium import webdriver
from bs4 import BeautifulSoup
from spyderpro.Connect.InternetConnect import Connect
from urllib.parse import urlencode


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
        :return iterable[{'信息':{"公众号": name, "微信号": public_pid},'文章列表':datalist},,,,,]
        """

        for pid in range(start, end, seq):
            url = 'https://www.wxnmh.com/user-{0}.htm'
            url = url.format(pid)
            result = self.reuqest_public(pid, url)

    def reuqest_public(self, pid: int, url: str) -> dict:
        """
        请求公众号数据接口
        :param pid:公众号数字id
        :param url: 首页链接
        :return  dict

        """
        result = self.get_detail_public_info(pid, url)
        return result

    def get_detail_public_info(self, pid: int, url: str) -> dict:
        """
        获取文章标题和链接
        :param pid:公众号数字id
        :param url: 首页链接
        :return  {'信息':{"公众号": name, "微信号": public_pid},'文章列表':datalist}
        """
        responsedata = dict()
        response = self.request.get(url=url, headers=self.headers)
        soup = BeautifulSoup(response.text, "lxml")
        keyword = soup.find(name="meta", attrs={"name": "keywords"}).get("content")
        info = keyword.split(",")
        name, public_pid = info[0], info[1]  # 公众号名字和微信号

        responsedata['信息'] = {"公众号": name, "微信号": public_pid}
        nav = soup.find(name="a", attrs={"class": "nav-link active"}).text
        articles_total_num = int(re.search("(\\d+)", nav, re.S).group(1))  # 总文章数
        pages = int(articles_total_num / 10.0 - 0.5)  # 文章总页数
        ''' #文章列表链接：https://www.wxnmh.com/user-pid-第几页文章.htm'''
        articles = soup.find_all(name="a", attrs={"target": "_blank", "href": re.compile(r"thread")})  # 该页所有文章
        datalist = list()
        for value in articles:
            href = value.get("href")  # 链接
            title = value.text  # 标题
            datalist.append({"标题": title, "链接": href})

        for page in range(2, pages):
            url = 'https://www.wxnmh.com/user-{0}-{1}.htm'.format(pid, page)
            result = self.get_all_article(url)

            for item in result:
                datalist.append(item)
        responsedata['文章列表'] = datalist
        return responsedata

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

    def search_public(self, public_pid: str):
        """在微小宝搜索公众号详细信息入口的信息
        :param public_pid:公众号账号
        :return dict->{"pid": pid, "href": href, "driver": driver}
        """
        query_string_parameters = {
            "kw": public_pid,
            "page": 1
        }
        driver = self.chrome()
        driver.get("https://data.wxb.com/searchResult?" + urlencode(query_string_parameters))
        response = driver.page_source
        soup = BeautifulSoup(response, 'lxml')
        href = soup.find(name='a', attrs={"href": re.compile("/details/postRead?")}).get('href')  # 获取链接
        pid = re.search("id=(.*)", href, re.I).group(1)
        url = "https://data.wxb.com" + href
        info = {"pid": pid, "url": url, "driver": driver}
        return info

    def request_public_data(self, driver, url):
        """获取该公众号的详细数据：平均阅读量，最高阅读量，平均点赞，最高点赞等
        :param driver:实例
        :param url:链接
        :return   {"总概况":{"头条平均阅读量": average_read, "最高阅读量": hight_read, "头条平均点赞数": average_like,
                               "最高点赞数": hight_like},"历史数据":[{"日期": day, "总阅读数": read_num_total, "总点赞数": top_like_num_total, "发表文章数":
                articles_total}]}
        """
        driver.get(url=url)
        response = driver.page_source
        soup = BeautifulSoup(response, 'lxml')
        average_read = int(soup.find(name="div", attrs={"data-reactid": "209"}).text)  # 头条平均阅读量
        hight_read = int(soup.find(name="div", attrs={"data-reactid": "217"}).text)  # 最高阅读量
        average_like = int(soup.find(name="div", attrs={"data-reactid": "225"}).text)  # 头条平均点赞数
        hight_like = int(soup.find(name="div", attrs={"data-reactid": "229"}).text)  # 最高点赞数
        responsedata = dict()
        responsedata['总概况'] = {"头条平均阅读量": average_read, "最高阅读量": hight_read, "头条平均点赞数": average_like,
                               "最高点赞数": hight_like}

        echartsData = re.search('"echartsData(.*?)}}', response, re.S).group(0)
        echartsData = "{%s}" % echartsData
        g = eval(echartsData)
        datas = g['echartsData']
        datalist = list()
        for key in datas.keys():
            data = datas[key]
            read_num_total = int(data['read_num_total'])  # 总阅读数
            top_like_num_total = int(data['top_like_num_total'])  # 总点赞数
            articles_total = int(data['articles_total'])  # 该天发表文章数
            day = key  # 日期
            datalist.append({"日期": day, "总阅读数": read_num_total, "总点赞数": top_like_num_total, "发表文章数":
                articles_total})
        responsedata['历史数据'] = datalist  # -> 一个月的数据量
        driver.close()
        return responsedata

    def get_public_keyword(self, pid):
        """获取关键词列表
        :param pid ：公众号id
        :return list[关键词]
        """
        href = "https://data.wxb.com/account/content/" + pid
        response = self.request.get(url=href, headers=self.headers)
        g = json.loads(response.text)
        keywords = list()
        for keyword in g['data']['hot_words']:
            keywords.append(keyword)
        return keywords

    @staticmethod
    def chrome():
        option = webdriver.ChromeOptions()
        option.add_argument('headless')
        driver = webdriver.Chrome(chrome_options=option)
        return driver
