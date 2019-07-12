import requests
import re
import json
from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.parse import urlencode
from spyderpro.portconnect.internetconnect import Connect
from spyderpro.instances.wechat import WechatPublic_Info, ArticleInfo, WechatSituation, ArticleKeyWord


class WechatPublic(Connect):
    # *****注意，微小宝请求方式发生了更改，还未修改相关数据获取

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
        :return iterable([WechatPublic_Info（page:页数，name:"公众号",pid "微信号",articles：'文章列表'）,,,,,])
        """

        for pid in range(start, end, seq):
            url = 'https://www.wxnmh.com/user-{0}.htm'
            url = url.format(pid)
            result = self.reuqest_public(pid, url)

            yield result

    def reuqest_public(self, pid: int, url: str) -> WechatPublic_Info:
        """
        请求公众号数据接口
        :param pid:公众号数字id
        :param url: 首页链接
        :return  dict

        """
        result: WechatPublic_Info = self.get_detail_public_info(pid, url)
        return result

    def get_detail_public_info(self, pid: int, url: str) -> WechatPublic_Info:
        """
        获取文章标题和链接
        :param pid:公众号数字id
        :param url: 首页链接
        :return  WechatPublic_Info
        """

        response = self.request.get(url=url, headers=self.headers)
        soup = BeautifulSoup(response.text, "lxml")
        keyword = soup.find(name="meta", attrs={"name": "keywords"}).get("content")
        info: list = keyword.split(",")
        name, public_pid = info[0], info[1]  # 公众号名字和微信号

        nav = soup.find(name="a", attrs={"class": "nav-link active"}).text
        articles_total_num = int(re.search("(\\d+)", nav, re.S).group(1))  # 总文章数
        pages = int(articles_total_num / 10.0 - 0.5)  # 文章总页数
        ''' #文章列表链接：https://www.wxnmh.com/user-pid-第几页文章.htm'''
        articles = soup.find_all(name="a", attrs={"target": "_blank", "href": re.compile(r"thread")})  # 该页所有文章
        datalist = list()
        '''第一页'''
        for value in articles:
            href = value.get("href")  # 链接
            title = value.text  # 标题
            datalist.append({"标题": title, "链接": href})
        wechatinfo = WechatPublic_Info(page=1, name=name, public_pid=pid, articlelist=iter(datalist))
        yield wechatinfo
        ''''第2页开始'''
        for page in range(2, pages):
            datalist = []

            url = 'https://www.wxnmh.com/user-{0}-{1}.htm'.format(pid, page)
            result = self.get_all_article(url)

            for item in result:
                datalist.append(item)
            wechatinfo = WechatPublic_Info(page=page, name=name, public_pid=pid, articlelist=iter(datalist))
            yield wechatinfo

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

    def request_public_data(self, pid) -> object:

        """获取该公众号的详细数据：平均阅读量，最高阅读量，平均点赞，最高点赞等
        :param driver:实例
        :param url:链接
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
        # return {"average_read": avg_read_num, "average_like": avg_like_num, "hight_read": max_read_latest,
        #         "hight_like": max_like_latest, "count_article": count_article_latest, "fans_num": fans_num_estimate,
        #         "data": datalist}
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

    def request_public_keyword(self, pid)->list:
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

# d = WechatPublic().get_all_public(4, 6)
# for i in d:
#     for j in i:
#         print(list(j.articles))
# w = WechatPublic()
# s = w.request_public_data('gh_41575c96fbf5')
# print(s)
# d = w.request_public_keyword('gh_41575c96fbf5')
