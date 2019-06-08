import csv
import time
from spyderpro.LocationBigData.PeopleFlow import ScencePeopleFlow

if __name__ == "__main__":
    f = open('/Users/darkmoon/Project/SpyderPro/spyderpro/testdata/ScenceData.csv', "r")

    read = csv.reader(f)
    pep = ScencePeopleFlow()
    title = read.__next__()
    filename = time.strftime("%Y-%d-%m", time.localtime(time.time()-3600*24))
    f2 = open("/Volumes/Tigo/数据集/%s.csv"% filename, 'a+', newline="")
    w = csv.writer(f2)
    for item in read:
        data = list()
        name = item[0]
        pid = item[1]
        data.append(name)
        for res in pep.peopleflow_info(pid):
            data.append(res)
        w.writerow(data)
        print("%s is ok" % name)
    f.close()
    f2.close()
