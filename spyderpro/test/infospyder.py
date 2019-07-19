import requests
import csv
import json
import time
from urllib.parse import urlencode

headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
    'cookie': 'guid=6072-edee-037a-6e69; UM_distinctid=1693d5c846c7c-0ab721669f9b9-10346655-1fa400-1693d5c846d34c; cna=eSABFd94dXgCAX1YGCe5+FfK; CNZZDATA1255827602=1510831518-1553064023-https%253A%252F%252Flbs.amap.com%252F%7C1553064023; _uab_collina=156092673765725951976118; key=bfe31f4e0fb231d29e1d3ce951e2c780; CNZZDATA1255626299=1966103709-1560921594-%7C1563519374; x5sec=7b22617365727665723b32223a2262303566626566386363663834343438333934336265323665633830643436664349506d78656b46454b7a6674366972334a6a4a3577453d227d; l=cBPF5jcPvcn7qwB3BOfCSQLXtzee4IRbzPVP2dSoNICP9m195-UfWZ3bg_8pCnNVL68eR3kkAObUBoT88y4th1ah0HfvQ_m5.; isg=BNnZ8f4R4HlUAb2mX2KW8MlF6MMfdALe3aCJMfuOs4B_AvuUQ7JD6V9UBIbSv2VQ',
    'amapuuid': '32ce72ba-2263-4a16-9713-f648228200f9'

}
f = open("/Users/darkmoon/Project/SpyderPr/datafile/scenceinfo.csv", 'r')
ff = open('/Users/darkmoon/Project/SpyderPr/datafile/info.csv', 'a+', newline='')
read = csv.reader(f)
write = csv.writer(ff)
# write.writerow(['城市','地名','标识','中心经度','中心维度','经纬度范围'])
read.__next__()
count = 0
for item in read:

    count += 1
    if count < 78:
        continue
    city = item[0]
    area = item[1]
    pid = item[2]
    lon = item[3]

    lat = item[4]
    param = {
        'query_type': 'TQUERY',
        'pagenum': 1,
        'cluster_state': 5,
        'need_utd': 'true',
        'utd_sceneid': 1000,
        'keywords': area,
    }
    url = 'https://ditu.amap.com/service/poiInfo?' + urlencode(param)
    print(url)
    response = requests.get(url=url, headers=headers).text
    g = json.loads(response)
    try:
        bounds = g['data']['poi_list'][0]['domain_list'][14]['value']
    except Exception as e:
        print(url)
        print(e, area)
        continue
    # write.writerow([city, area, pid, lon, lat, bounds])
    print(area)
    time.sleep(10)
f.close()

# ，欢乐谷，锦绣中华·中国民俗文化村，小梅沙度假村，杨梅坑，南昆山温泉大观园，锦江温泉旅游度假区，肇庆星湖风景名胜区,忠信广场,荣基国际广场,铜锣湾广场
# 南湾猴岛生态旅游景区,雅居乐海南清水湾,乐东商业步行街,商贸购物广场,凤凰商业步行街,南昌北站,龙湾温泉度假村
