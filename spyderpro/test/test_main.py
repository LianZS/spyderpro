import csv
import datetime
from spyderpro.LocationBigData.PeopleFlow import ScencePeopleFlow
from spyderpro.WeatherModel.WeatherLishi import WeatherHistory
from spyderpro.WeatherModel.Weather import WeatherForect
from concurrent import futures
from spyderpro.LocationBigData.PlacePeople import PlaceFlow
from spyderpro.TrafficData.BaiduTraffic import BaiduTraffic


def test_weather():
    w = WeatherHistory()
    datalist = w.get_province_link()
    datalist = w.get_city_past_link(url=datalist[7]['url'])
    w.get_city_all_partition(datalist[0]['url'])


def test_placeflow():
    p = PlaceFlow()
    it = p.complete_heatdata("2019-06-28", "13:00:00", 5381)
    for i in it:
        print(i)


def get_count(name, region_id):
    executor = futures.ThreadPoolExecutor(max_workers=4)
    p = PlaceFlow()
    datelist = dateiter(region_id)
    f = open('/Users/darkmoon/Project/SpyderPr/static/' + name + ".csv", "a+", newline="")
    w = csv.writer(f)
    tasks = executor.map(lambda x: p.count_headdata(str(x[0]), str(x[1]), x[2]), datelist)
    for item in tasks:
        num = item['num']
        if num == 0:
            continue
        date = item['date']
        write(w, date, num)


def write(writeobj, date, num):
    writeobj.writerow([date, num])


def dateiter(region_id):

    inittime = datetime.datetime(2017, 1, 1, 0, 0, 0)
    timedelta = datetime.timedelta(minutes=5)
    while 1:
        inittime = inittime + timedelta
        if inittime.year == 2019 and inittime.month == 6 and inittime.day == 28:
            break
        yield inittime.date(), inittime.time(), region_id


if __name__ == "__main__":
    if __name__ == "__main__":
        file = open("/Users/darkmoon/Project/SpyderPr/spyderpro/testdata/region_id.csv", "r")
        r = csv.reader(file)
        r.__next__()
        for item in r:
            name = item[0]
            pid = item[1]
            get_count(name, pid)

    # test_placeflow()
    # f = open('/Users/darkmoon/Project/SpyderPro/spyderpro/testdata/ScenceData.csv', "r")
    #
    # read = csv.reader(f)
    # pep = ScencePeopleFlow()
    # title = read.__next__()
    # filename = time.strftime("%Y-%d-%m", time.localtime(time.time() - 3600 * 24))
    # f2 = open("/Volumes/Tigo/数据集/%s.csv" % filename, 'a+', newline="")
    # w = csv.writer(f2)
    # for item in read:
    #     data = list()
    #     name = item[0]
    #     pid = item[1]
    #     data.append(name)
    #     for res in pep.peopleflow_info(pid):
    #         data.append(res)
    #     w.writerow(data)
    #     print("%s is ok" % name)
    # f.close()
    # f2.close()
    pass
