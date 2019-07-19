import csv


class City:
    def __init__(self, city, citycode, yearcode, lat, lon):
        self.city = city
        self.citycode = citycode
        self.yearcode = yearcode
        self.lat = lat
        self.lon = lon


if __name__ == "__main__":
    f = open('/Users/darkmoon/Project/SpyderPr/datafile/baiducity.csv', 'r')
    ff = open('/Users/darkmoon/Project/SpyderPr/datafile/gaodecity.csv', 'r')
    r1 = csv.reader(f)
    r2 = csv.reader(ff)
    r1.__next__()
    info1=[]
    info2=[]
    l1 = set()
    l2=set()
    for item in r1:
        l1.add(item[0])
    for item in r2:
        l2.add(item[1])
        info2.append({item[1]:item[0]})

    jiaocha = l1.intersection(l2)
    dif = l2.difference(l1)
    print(dif)
    l = []
    for item in jiaocha:
        for dic in info2:
            if item in dic.keys():
                l.append(dic)
    f = open('/Users/darkmoon/Project/SpyderPr/datafile/baiducity.csv', 'r')

    r1= csv.reader(f)
    r1.__next__()
    objs = []

    for item in r1:
        city = item[0]
        citycode= item[1]
        lat=item[2]
        lon=item[3]
        c= None
        for dic in l:
            if city in dic.keys():
                c =City(city=city,citycode=citycode,yearcode=list(dic.values())[0],lat=lat,lon=lon)
                break

        if not  c:
            c = City(city=city, citycode=citycode, yearcode=0, lat=lat, lon=lon)

        objs.append(c)
    f.close()
    f=open('/Users/darkmoon/Project/SpyderPr/datafile/trafficinfo.csv','a+',newline='')
    w = csv.writer(f)
    w.writerow(['城市名','城市id','维度','经度','年度id'])
    for obj in objs:
        w.writerow([obj.city,obj.citycode,obj.lat,obj.lon,obj.yearcode])
    f.close()


