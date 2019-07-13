import pymysql
import random
import datetime
from spyderpro.managerfunction.setting import *
from threading import Thread
from threading import Semaphore
import queue


def insert(scencename):
    name = random.choices(nameslist)[0]
    scenceid = values[name]
    datetimelist = dateiter()
    for date, detail in datetimelist:
        sql = "insert into digitalsmart.scenceflow (name, scenceid, date,detailtime, num) values ('%s','%d','%s'," \
              "'%s','%d')" % (
                  scencename, scenceid, date, detail, random.randint(1, 10000))
        q.put(sql)
    semaphore.release()


def save():
    cursor = Connection.cursor()

    while 1:
        cmd = q.get()
        try:
            cursor.execute(cmd)
            Connection.commit()
        except Exception as e:
            print(e)

            Connection.rollback()


def dateiter():
    inittime = datetime.datetime(2017, 5, 22, 16, 30, 0)
    timedelta = datetime.timedelta(minutes=5)
    while 1:
        inittime = inittime + timedelta
        if inittime.year == 2019 and inittime.month == 7 and inittime.day == 8:
            break
        yield str(inittime.date()), str(inittime.time())


Connection = pymysql.connect(host=host, user=user, password=password,
                             database='digitalsmart',
                             port=port)

values = {'平遥古城': 1174, '五台山风景名胜区': 1376, '嵩山国家风景名胜区': 1378, '泰山': 1375, '崂山风景区': 1356, '张家界武陵源风景名胜区': 1377, '庐山': 1352,
          '汕头南澳岛旅游区': 1364, '瘦西湖': 248, '玄武湖公园': 1222, '灵山胜境': 516, '中山陵园': 1350, '明孝陵景区': 1347, '周庄': 405,
          '同里古镇游览区': 1349, '常州中华恐龙园': 232, '连云港花果山风景区': 1346, '苏州太湖园博园': 1348, '香河第一城': 1395, '蔚县暖泉古镇': 1396,
          '正定隆兴寺': 1381, '吴桥杂技大世界': 1409, '太舞滑雪场': 1399, '张家口万龙滑雪场': 1398, '长城岭滑雪场': 1397, '长春南湖公园': 123, '净月潭': 98,
          '长春公园': 1441, '胜利公园': 1435, '哈尔滨儿童公园': 1445, '庙香山': 1444, '长春莲花山': 1436, '武侯祠': 199, '宽窄巷子': 105,
          '成都人民公园': 1319, '天府广场': 1320, '大熊猫繁育研究基地': 32, '杜甫草堂': 287, '成都欢乐谷': 80, '成都动物园': 332, '宝资山森林公园': 1314,
          '幸福梅林景区': 1321, '颐和园': 214, '故宫': 54, '圆明园': 222, '北京动物园': 12, '天坛': 189, '玉渊潭公园': 1411, '古北水镇': 1310,
          '奥林匹克森林公园': 2, '北京北海公园': 10, '陶然亭公园': 1414, '天安门广场': 185, '北京欢乐谷': 79, '北京龙潭公园': 1412, '北京香山': 206,
          '雍和宫': 217, '龙庆峡': 1413, '重庆磁器口': 22, '洪崖洞': 69, '仙女山': 1428, '重庆市朝天门广场': 18, '金石滩': 1380, '大连森林动物园': 1328,
          '大连星海公园': 208, '大连劳动公园': 1327, '老虎滩海洋公园': 107, '西湖': 1343, '千岛湖': 402, '西溪湿地': 202, '杭州宋城': 178, '杭州清河坊': 316,
          '杭州动物园': 1339, '龙门古镇': 344, '杭州野生动物世界': 398, '浙西大峡谷': 1345, '广州白云山': 5, '长隆野生动物世界': 228, '广州动物园': 56,
          '广州长隆欢乐世界': 227, '广州塔': 57, '上海迪士尼度假区': 1265, '上海城隍庙': 1357, '上海东方明珠': 1181, '上海人民公园': 1360, '上海动物园': 158,
          '上海科技馆': 457, '上海野生动物园': 472, '豫园': 220, '上海欢乐谷': 78, '上海泰晤士小镇': 1361, '世界之窗': 173, '深圳莲花山公园': 1371,
          '中国民俗文化村': 1373, '仙湖植物园': 205, '欢乐海岸': 1368, '大梅沙': 386, '深圳野生动物园': 495, '深圳东部华侨城': 1365, '深圳欢乐谷': 77,
          '深圳凤凰山': 1366}
nameslist = list(values.keys())
semaphore = Semaphore(10)
inittime = datetime.datetime(2017, 5, 22, 16, 30, 0)
q = queue.Queue(10)
Thread(target=save, args=()).start()
for scencename in nameslist:
    semaphore.acquire()
    print(scencename)
    Thread(target=insert, args=(scencename,)).start()
