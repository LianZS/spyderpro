import requests
import re
import datetime
import time
import json
import csv
import sys
import os
import threading
from queue import Queue
from urllib.parse import urlencode

area_data = [
# [4904,'坣岗荔枝公园'],
# [4905,'大梅沙海滨公园'],
# [4906,'东部华侨城'],
# [4910,'凤凰山森林公园'],
# [5532,'小梅沙度假村'],
# [8493,'欢乐海岸'],
# [8520,'西丽动物园'],
# [8522,'莲花山公园'],
# [8528,'梧桐山'],
# [9362,'杨梅坑'],
# [10107,'红树林公园'],
# [18343,'荔香公园'],
# [18346,'深圳海上世界'],
# [8,'广州长隆'],
# [512,'广州站'],
# [1050,'南昆山生态旅游区'],
# [1074,'南昆山温泉大观园'],
# [1057,'西樵山风景名胜区'],
# [4884,'李小龙乐园'],
# [1059,'圆明新园'],
# [4898,'白莲洞公园'],
# [1060,'中山詹园'],
# [6118,'中山市火车站'],
# [1061,'塘口立园'],
# [1082,'锦江温泉旅游度假区'],
# [1073,'曹溪温泉假日度假村'],
# [4927,'风度名城'],
# [4929,'威尼国际广场'],
# [1087,'肇庆星湖风景名胜区'],
# [1101,'海陵岛大角湾风景名胜区'],
# [1187,'汕尾玄武山旅游区'],
# [4855,'玄武山旅游区'],
# [1188,'礐石风景名胜区'],
# [4859,'揭阳潮汕国际机场'],
# [4991,'榕江西湖公园'],
# [4864,'兆康时代广场'],
# [4865,'忠信广场'],
# [4870,'金沙湾观海长廊'],
# [4871,'荣基国际广场'],
# [4881,'罗定人民体育场'],
# [4882,'同富商业中心'],
# [4989,'绿岛山庄'],
# [1280,'明月山温泉风景名胜区'],
# [1281,'天沐江西明月山温泉度假村'],
# [1686,'龙虎山地质公园'],
# [535,'西安站'],
# [627,'西安咸阳国际机场'],
# [1002,'乾陵博物馆'],
# [1003,'延安革命纪念馆'],
# [1004,'枣园革命旧址'],
# [1009,'华山风景名胜区'],
# [1679,'法门寺法门寺旅游区'],
# [5649,'金丝峡景区'],
# [542,'太原站'],
# [555,'太原武宿国际机场'],
# [982,'王家大院'],
# [1145,'绵山风景名胜区'],
# [1006,'普救寺'],
# [1007,'解州关帝庙'],
# [1134,'天下第一门'],
# [1626,'黄河壶口瀑布'],
# [1398,'山西应县木塔景区'],
# [543,'呼和浩特东站'],
# [544,'呼和浩特白塔国际机场'],
# [1108,'响沙湾旅游景区'],
# [5664,'水洞沟文化遗址'],
# [1117,'广宗寺'],
# [1381,'喀喇沁亲王府'],
# [1560,'阿斯哈图花岗岩石林园区'],
# [1408,'呼和诺尔旅游景区'],
# [1410,'满洲里套娃广场'],
# [1425,'格根塔拉草原旅游区'],
# [1492,'阿尔山海神圣泉旅游度假区'],
# [1495,'大青沟'],
# [1605,'维信国际高尔夫度假村'],
# [5356,'乌海湖'],
# [5497,'乌海植物园'],
# [546,'兰州站'],
# [553,'兰州中川机场'],
# [940,'拉卜楞寺'],
# [1631,'冶力关风景区'],
# [944,'嘉峪关长城文化旅游景区'],
# [945,'鸣沙山月牙泉风景名胜区'],
# [1681,'阳关景区'],
# [947,'松鸣岩风景名胜区'],
# [948,'万象洞'],
# [1142,'官鹅沟自然风景区'],
# [1154,'西狭颂景区'],
# [960,'大佛寺'],
# [961,'武威沙漠公园'],
# [962,'武威文庙'],
# [963,'神州荒漠野生动物园'],
# [964,'景泰黄河石林风景旅游区'],
# [1010,'麦积山风景区'],
# [1140,'贵清山旅游风景区'],
# [1161,'遮阳山旅游风景区'],
# [549,'乌鲁木齐地窝堡国际机场'],
# [550,'乌鲁木齐站'],
# [934,'龟兹绿洲生态园'],
# [1152,'库车原世袭回部亲王府'],
# [935,'金沙滩旅游度假区'],
# [936,'天山天池风景区'],
# [953,'新疆兵团军垦博物馆'],
# [959,'锡伯民俗风情园'],
# [5621,'那拉提旅游风景区'],
# [1114,'吐鲁番葡萄沟风景区'],
# [1121,'怪石峪风景区'],
# [1135,'喀什噶尔老城景区'],
[554,'石家庄正定国际机场'],
[612,'石家庄站'],
[1590,'嶂石岩风景名胜区'],
[1356,'香河第一城'],
[1411,'廊坊市文化艺术中心公园'],
[1382,'普陀宗乘之庙'],
[1383,'承德避暑山庄'],
[1559,'金山岭长城旅游区'],
[1396,'白洋淀风景区'],
[1553,'野三坡白草畔景区'],
[1426,'黄龙山庄'],
[1584,'万龙滑雪场'],
[1525,'崆山白云洞'],
[1530,'娲皇宫'],
[1579,'北戴河·集发观光园'],
[1646,'吴桥杂技大世界'],
[5650,'清东陵景区'],
[586,'长沙黄花国际机场'],
[1619,'岳麓山风景名胜区'],
[1017,'南岳衡山风景区'],
[6180,'南岳大庙'],
[1023,'任弼时纪念馆'],
[1151,'岳阳楼风景区'],
[1024,'彭德怀纪念馆'],
[6179,'毛泽东同志纪念馆'],
[1036,'宝峰湖风景区'],
[1037,'黄龙洞风景区'],
[1046,'九嶷山舜帝陵风景区'],
[1125,'桃花源风景区'],
[1138,'茅岩河九天洞风景区'],
[1285,'炎帝陵'],
[1616,'益阳奥林匹克公园'],
[1622,'苏仙岭风景名胜区'],
[5646,'东江湖风景旅游区'],
[5357,'湄江国家地址公园'],
[605,'武汉站'],
[975,'武当山风景区'],
[1029,'神农架神农顶风景区'],
[1030,'神农架红坪景区'],
[1031,'古隆中'],
[1032,'三峡车溪土家民俗旅游区'],
[1147,'神农溪纤夫文化旅游区'],
[1049,'邓小平故里旅游区'],
[1123,'夕佳山景区'],
[1136,'兴文世界地质公园'],
[1130,'七曲山风景区'],
[1144,'窦圌山景区'],
[653,'贵阳龙洞堡国际机场'],
[4503,'人民广场'],
[876,'龙宫风景名胜区'],
[5665,'黄果树大瀑布景区'],
[897,'遵义会议会址'],
[902,'贵州百里杜鹃风景名胜区'],
[5666,'荔波樟江风景名胜区'],
[749,'天津站'],
[806,'天津滨海国际机场'],
[760,'上海虹桥国际机场'],
[763,'上海浦东国际机场'],
[771,'杭州萧山国际机场'],
[772,'杭州站'],
[1300,'竹海风景区'],
[4393,'湖州站'],
[1601,'南雁荡山国家重点风景名胜区'],
[6202,'温州火车站'],
[1630,'长屿硐天风景名胜区'],
[1636,'江南长城景区'],
[4201,'龙泉凤羽休闲山庄'],
[4727,'清漾景区'],
[4395,'嘉兴站'],
[4424,'朱家尖国际沙雕艺术广场'],
[4425,'乌石塘景区'],
[6074,'绍兴市城市广场'],
[6075,'绍兴市天主堂'],
[774,'合肥汽车客运总站'],
[1286,'徽园'],
[1178,'黄山风景区'],
[5634,'黄山皖南古村落（西递）'],
[1183,'恩龙山庄生态旅游度假区'],
[5635,'绩溪龙川景区'],
[1261,'天柱山旅游区'],
[1262,'石台牯牛降风景区'],
[1624,'九华山风景区'],
[1303,'马仁奇峰森林风景区'],
[1304,'王稼祥纪念园'],
[1349,'天堂寨风景区'],
[1350,'万佛湖风景区'],
[1541,'阜阳生态乐园'],
[5636,'颍上八里河景区'],
[1566,'八公山风景区'],
[1617,'采石景区'],
[786,'首都国际机场'],
[4307,'新中关购物中心'],
[5381,'北京欢乐谷'],
[790,'济南火车站'],
[791,'济南遥墙国际机场'],
[1507,'孟庙孟府'],
[5614,'明故城（三孔）旅游区'],
[1522,'五莲山风景区'],
[1527,'聊城东昌湖旅游区'],
[1537,'台儿庄古城'],
[1576,'蒙山旅游区平邑龟蒙景区'],
[1577,'蒙山国家森林公园'],
[1582,'沂山国家森林公园'],
[1586,'中国陶瓷馆'],
[1652,'原山国家森林公园'],
[1589,'房干生态旅游区'],
[1592,'泰山风景区'],
[1628,'刘公岛风景名胜区'],
[1687,'赤山风景名胜区'],
[4352,'青岛十梅庵风景区'],
[5903,'青岛市火车站'],
[805,'沈阳桃仙国际机场'],
[5711,'沈阳奥体中心'],
]

class Connect:

    def connect(self, par: str, url: str) -> dict:
        """网络连接
        :param par:正则表达式
        :param url:请求链接
        :return json
        """

        data = self.request.get(url=url, headers=self.headers)
        if data.status_code != 200:
            print("%s请求--error:网络出错" % url)
            raise ConnectionError('网络连接中断')
        try:
            if par is not None:
                result = re.findall(par, data.content.decode('gbk'), re.S)[0]
            else:
                result = data.text
        except UnicodeDecodeError:
            result = re.findall(par, data.text, re.S)[0]
        data = json.loads(result)
        assert isinstance(data, (dict, list))
        return data


class ParamTypeCheck():
    @staticmethod
    def type_check(param, param_type):
        """
        参数类型检查
        :rtype:
        :param param:
        :param param_type:
        :return:
        """
        assert isinstance(param, param_type), "the type of param is wrong"


class PlaceInterface(Connect, ParamTypeCheck):
    instance = None
    instance_flag: bool = False

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    # 获取所有省份
    def get_allprovince(self) -> list:
        """
        获取所有省份
        :return: list
        """
        href = "https://heat.qq.com/api/getAllProvince.php?sub_domain="
        par: str = None
        g = self.connect(par, href)
        data = [value["province"] for value in g]
        return data

    # 所有城市
    def get_allcity(self, province: str) -> list:
        """
        获取省份下所有城市
        :param province: 省份名
        :return: list[{"province": , "city":}，，]
        """
        # 这里不需要quote中文转url，因为后面的urlencode自动会转

        parameter = {
            "province": province,
            "sub_domain": ''
        }
        href = "https://heat.qq.com/api/getCitysByProvince.php?" + urlencode(parameter)
        par: str = None
        g = self.connect(par, href)
        results = [{"province": province, "city": value["city"]} for value in g]
        return results

    def get_regions_bycity(self, province: str, city: str) -> list:
        """
        获取城市下所有地区信息标识，关键id

        :type province: str
        :type city:str
        :param province:省份
        :param city:城市
        :return  list[{"place": , "id": },,,,]
        """
        self.type_check(province, str)
        self.type_check(city, str)
        parameter = {
            'province': province,
            'city': city,
            'sub_domain': ''
        }

        href = "https://heat.qq.com/api/getRegionsByCity.php?" + urlencode(parameter)

        par: str = None
        g = self.connect(par, href)
        datalist = list()
        for value in g:
            placename = value['name']  # 地点
            placeid = value["id"]  # id
            dic = {"place": placename, "id": placeid}
            datalist.append(dic)
        return datalist
        # range表示数据间隔，最小1,region_name是地点名字,id是景区pid


class PlaceFlow(PlaceInterface):
    """
    获取地区人口分布情况数据
    """

    def __init__(self, user_agent: str = None):

        if not PlaceFlow.instance_flag:
            PlaceFlow.instance_flag = True
            self.headers = dict()
            if user_agent is None:
                self.headers[
                    'User-Agent'] = 'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'

            else:
                self.headers['User-Agent'] = user_agent
            self.headers['Host'] = 'heat.qq.com'

            self.request = requests.Session()

    def request_heatdata(self, url: str):
        """
        网络请求
        :param url:
        :return:json
        """

        response = self.request.get(url=url, headers=self.headers)
        if response.status_code == 200:
            g = json.loads(response.text)
            return g
        else:
            return None

    def __get_heatdata_bytime(self, date: str, datetim: str, region_id: int):
        # self.type_check(region_id, int)
        paramer = {
            'region_id': region_id,
            'datetime': "".join([date, ' ', datetim]),
            'sub_domain': ''
        }

        url = "https://heat.qq.com/api/getHeatDataByTime.php?" + urlencode(paramer)
        g = self.request_heatdata(url)

        return g

    def count_headdata(self, date: str, datetim: str, region_id: int):
        """
        某一时刻的人数有多少
        :param date:日期：格式yyyy-mm-dd
        :param datetim:时间：格式hh:MM:SS
        :param region_id:地区唯一表示
        :return:总人数
        """
        g = self.__get_heatdata_bytime(date, datetim, region_id)
        if not g:
            return None
        count = sum(g.values())  # 总人数
        data = {"date": "".join([date, ' ', datetim]), "num": count}
        return data

    def complete_heatdata(self, date: str, datetim: str, region_id: int):
        """
           某一时刻的人数以及分布情况
           :param date:日期：格式yyyy-mm-dd
           :param datetime:时间：格式hh:MM:SS
           :param region_id:地区唯一表示
           :return:dict格式：{"lat": lat, "lng": lng, "num": num}->与中心经纬度的距离与相应人数
           """
        g = self.__get_heatdata_bytime(date, datetim, region_id)

        coords = map(self.deal_coordinates, g.keys())  # 围绕中心经纬度加减向四周扩展
        numlist = iter(g.values())

        for xy, num in zip(coords, numlist):
            lat = xy[0]
            lng = xy[1]
            yield {"lat": lat, "lng": lng, "num": num}

    @staticmethod
    def deal_coordinates(coord):
        if coord == ',':
            return (0, 0)
        escape = eval(coord)

        return escape


class CeleryThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, *, daemon=None):
        threading.Thread.__init__(self)
        self._target = target
        self._args = args

    def run(self):
        result = self._target(*self._args)
        if result:
            data_queue.put(result)
        semaphore.release()


def get_count(region_id):
    p = PlaceFlow()
    datelist = dateiter(region_id)

    global data_file
    global wf
    place = PlaceFlow()
    func = place.count_headdata
    wait.acquire()
    fileclose.put(1)
    print("start")
    data_file = open(file_path, 'a+', newline="")
    wf = csv.writer(data_file)

    for date, datetim, region_id in datelist:
        semaphore.acquire()
        t = CeleryThread(target=func, args=(date, datetim, regin_id))
        t.start()
    print("wait")
    fileclose.join()
    print("close")
    wait.release()
    time.sleep(10)
    data_file.close()


def write():
    while 1:
        try:
            data = data_queue.get(timeout=5)
        except Exception as e:
            fileclose.get()
            fileclose.task_done()

            continue
        date = data['date']

        num = data['num']
        wf.writerow([date, num])
        data_file.flush()


def dateiter(region_id):
    inittime = datetime.datetime(2017, 1, 1, 0, 0, 0)
    timedelta = datetime.timedelta(minutes=5)
    flag = 0

    if not last:
        flag = 1
    while 1:
        inittime = inittime + timedelta
        if inittime.year == 2019 and inittime.month == 7 and inittime.day == 8:
            break
        if lastdate == str(inittime.date()) and lastdatetim == str(inittime.time()) and not flag:
            flag = 1
            continue
        if flag:
            yield str(inittime.date()), str(inittime.time()), region_id


base_dir = os.getcwd()
sys.path[0] = base_dir
semaphore = threading.Semaphore(10)
fileclose = Queue(1)
wait = threading.Semaphore(1)
data_queue = Queue(maxsize=10)
global data_file
global wf  # csv实例

if __name__ == "__main__":


    dir_path = os.path.join(base_dir, "FILE")
    try:
        os.mkdir(dir_path)
    except FileExistsError:
        pass
    CeleryThread(target=write, args=()).start()  # 实时数据处理
    for item in area_data:
        regin_id = item[0]
        name = item[1]
        file_path = os.path.join(dir_path, name + ".csv")
        last = None
        lastdate = None
        lastdatetim = None
        if os.path.exists(file_path):
            ff = open(file_path, 'r')
            data = csv.reader(ff)
            for row in data:
                last = row[0]
            if last:
                lastdate, lastdatetim = last.split(' ')  # 最后一行数据
            ff.close()

        print(name)
        get_count(regin_id)
