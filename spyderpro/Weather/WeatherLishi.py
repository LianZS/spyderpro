import requests
import re
import csv
from concurrent import futures
from bs4 import BeautifulSoup
from multiprocessing import Pool as MP

import time, random
from threading import Lock

'''获取2k多个城市的历史天气情况'''


class WeatherData(object):
    def __init__(self):
        self.s = requests.Session()
        self.headers = {
            'Host': 'www.tianqihoubao.com',
            'User-Agent': 'Mozilla/5.0 (Macinto¬sh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/71.0.3578.98 Safari/537.36'
        }
        self.use = ['Mozilla/5.0 (X11; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0',
                    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:64.0) Gecko/20100101 Firefox/64.0',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:10.0) Gecko/20100101 Firefox/62.0',
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/71.0.3578.98 Safari/537.36',
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134']

    # 获取每个省份的链接
    def getprovince(self, writepath) -> bool:
        """
        获取每个省份的链接入口
        :param writepath: 写入文件地址
        :return: bool
        """
        url = 'http://www.tianqihoubao.com/'
        f = open(writepath, 'a+', newline="")
        write = csv.writer(f)
        list_data = self.s.get(url=url, headers=self.headers)
        soup = BeautifulSoup(list_data.text, 'lxml')
        soup.prettify()
        result = soup.find_all(name='a', href=re.compile('weather/province'))
        pre_url = 'http://www.tianqihoubao.com/'
        for res in result:
            url_lis = []
            lis = []
            url_lis.append(pre_url)
            url_lis.append(res['href'])
            url = ''.join(url_lis)  # 链接拼接
            lis.append(res.string)  # 省份名字
            lis.append(res['title'])  # 标签的tiltle
            lis.append(url)
            write.writerow(lis)
        f.close()
        return True

    def getcity_past_month_data_link(self, url):
        """
         获取每个省份下面的城市过去一个月的天气情况链接,如
        :param url:
        :return:iterable(dict)
        dict->{"name":地名,"url":链接}
            """
        # url = 'http://www.tianqihoubao.com/weather/province.aspx?id=340000'
        data = self.s.get(url=url, headers=self.headers)
        sounp = BeautifulSoup(data.text, 'lxml')
        result = sounp.find_all(name='a', href=re.compile('top/'))
        pre_url = 'http://www.tianqihoubao.com/weather/'
        for res in result:
            url_lis = []
            dic = dict()
            url_lis.append(pre_url)
            url_lis.append(res['href'])
            url = ''.join(url_lis)  # 链接拼接
            dic['name'] = res.string  # 省份名字
            dic['url'] = url  # 链接
            yield dic

    # 获取进入每个城市具体的区域--***省份***---链接入口
    def getDetail_LINK(self):
        url = 'http://www.tianqihoubao.com/lishi/'
        data = self.s.get(url=url, headers=self.headers)
        pre_url = 'http://www.tianqihoubao.com/'
        sounp = BeautifulSoup(data.content, 'lxml')  # 此处不要使用data.text，会出现乱码，改用response保证原有样子
        sounp.prettify()
        pid = 110
        i = 1
        for res in sounp.find_all(name='a', href=re.compile('^/lishi.*[htm]$')):
            url_lis = []
            l = []
            url_lis.append(pre_url)
            url_lis.append(res['href'])
            url = ''.join(url_lis)  # 链接拼接
            l.append(res.string)  # 省份名字
            l.append(res['title'])  # a标签的tiltle
            l.append(url)
            pid += 1
            if pid >= 111:

                self.getCityAll_PastLink(url, pid)
            else:
                continue

    # 获取省份下所有***城市分区***链接

    def getCityAll_PastLink(self, url, pid):

        data = self.s.get(url=url, headers=self.headers)
        pre_url = 'http://www.tianqihoubao.com/'
        sounp = BeautifulSoup(data.content, 'lxml')  # 此处不要使用data.text，会出现乱码，改用response保证原有样子
        sounp.prettify()
        pool = MP(processes=4)
        pid = str(pid)
        i = 0
        for res in sounp.find_all(name='dd'):
            res = res.find_all(name='a')
            lis = []
            for r in res:
                if i == 0:
                    print("城市：%s的分区有" % r.string)
                url_lis = []
                l = []
                url_lis.append(pre_url)
                url_lis.append(r['href'])
                url = ''.join(url_lis)  # 链接拼接
                l.append(url)
                p = pid + str(i + 1)  # 标记城区id
                i += 1
                # if i <= 27:
                #     continue
                # 存放链接的文件地址
                path = "/Volumes/Tigo/DataBase/" + r['title'] + ".csv"
                l.append(path)
                l.append(p)
                l.append(r['title'])
                lis.append(l)
                #
                pool.apply_async(func=self.getAllCity_Partition, args=(l,))
        pool.close()  # 记得是写在最外层，否则会引起pool error
        pool.join()

    # 获取城市分区下所有月份的历史天气链接
    def getAllCity_Partition(self, lis):
        print("%s开始执行" % lis[3])

        f = open(lis[1], 'r')
        reader = csv.reader(f)
        f2 = open("/Volumes/Tigo/DataBaseDetail/" + lis[2] + '.csv', 'a+')  # 以pid作为文件名
        write = csv.writer(f2)
        l = [lis[3]]
        write.writerow(l)  # 先写入城区名
        date = ['日期', '天气状况', '气温', '风力风向']
        write.writerow(date)
        pool = futures.ThreadPoolExecutor(2)
        l = []
        lock = Lock()

        for item in reader:
            l.append([item[1], write, f2, lock])
        pool.map(self.intoAreaLink, l)

        print("%s执行结束" % lis[3])

    # 进入每个区域某个月的天气数据
    def intoAreaLink(self, lis):

        headers = {
            'Host': 'www.tianqihoubao.com',
            'User-Agent': random.choice(self.use)
        }
        url = lis[0]
        write = lis[1]
        f = lis[2]
        lock = lis[3]

        try:
            data = requests.get(url=url, headers=headers)
        except ConnectionResetError:
            print("断网了")
            time.sleep(1800)
            self.intoAreaLink(lis)

        except ConnectionError:
            print("该链接链接出现问题%s" % str(lis))
            time.sleep(180)
            self.intoAreaLink(lis)
        except Exception as e:
            print(e)
            print("%s出问题了" % str(lis))
            return 0

        sounp = BeautifulSoup(data.text, 'lxml')  # 此处不要使用data.text，会出现乱码，改用response保证原有样子
        sounp.prettify()
        result = sounp.find_all(name='td')
        count = 0
        l = []

        for res in result[4:]:  # 将date这个说明跳过

            if count == 0:  # 每一组4个里的第一个含有a标签，不能直接string
                l.append(re.sub('\s', '', str(res.find(name='a').string)))
            else:
                l.append(re.sub("\s", '', str(res.string)))
            count += 1
            if count == 4:
                write.writerow(l)
                lock.acquire()
                f.flush()
                lock.release()
                l = []
                count = 0

        print("ok")

    # 设置省份下有那些城市并记录ip
    def GetCityOfProvince(self):
        url = 'http://www.tianqihoubao.com/lishi/'
        data = self.s.get(url=url, headers=self.headers)
        pre_url = 'http://www.tianqihoubao.com/'
        sounp = BeautifulSoup(data.content, 'lxml')  # 此处不要使用data.text，会出现乱码，改用response保证原有样子
        sounp.prettify()
        pid = 110
        i = 1
        f = open("/Users/darkmoon/PycharmProjects/MyWeb/Scenic/material/WeatherOfCity.csv", "a+", newline='')
        w = csv.writer(f)
        for res in sounp.find_all(name='a', href=re.compile('^/lishi.*[htm]$')):
            url_lis = []
            l = []
            url_lis.append(pre_url)
            url_lis.append(res['href'])
            url = ''.join(url_lis)  # 链接拼接
            l.append(res.string)  # 省份名字
            l.append(res['title'])  # a标签的tiltle
            l.append(url)
            pid += 1
            if pid >= 111:
                lis = []
                lis.append({res.string: pid})

                data = self.s.get(url=url, headers=self.headers)

                pre_url = 'http://www.tianqihoubao.com/'
                sounp = BeautifulSoup(data.content, 'lxml')  # 此处不要使用data.text，会出现乱码，改用response保证原有样子

                sounp.prettify()
                strpid = str(pid)
                i = 0
                for res in sounp.find_all(name='dd'):
                    res = res.find_all(name='a')
                    for r in res:
                        if i == 0:
                            print("城市：%s的分区有" % r.string)
                        p = strpid + str(i + 1)  # 标记城区id
                        i += 1
                        lis.append({r['title'][:-8]: p})

                w.writerow(lis)
                f.flush()
        f.close()

    def GetPID(self):
        href = 'http://www.tianqihoubao.com/aqi/'
        data = self.s.get(url=href, headers=self.headers)
        soup = BeautifulSoup(data.content, 'lxml')
        result = soup.find_all(name='dd')
        l = []
        for item in result:
            for name in item.find_all(name="a"):
                name = name.text.strip(" ")
                l.append(name)
        return l


def main():
    w = WeatherData()
    result = w.getcity_past_month_data_link("")
    for i in result:
        print(i)
    # w.getDetail_LINK()
    # w.GetCityOfProvince()
    w.GetPID()


if __name__ == "__main__":
    main()
