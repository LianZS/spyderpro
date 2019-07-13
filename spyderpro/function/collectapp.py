import requests
import json
import csv
from threading import Thread, Semaphore
from queue import Queue

semaphore = Semaphore(10)
q = Queue(10)
f = open('/data/Flow/APP/app.csv', 'a+', newline='')
w = csv.writer(f)


def collectapp(pid):
    url = ''.join(['http://mi.talkingdata.com/app/trend/appRank.json?appId=', str(pid),
                   '&dateType=m&date=2018-11-01&typeId=101000'])
    d = requests.get(url=url)
    semaphore.release()
    g = json.loads(d.text)

    try:
        result = g['appInfo']
    except KeyError:
        return None

    q.put({"pid": pid, "app": result['appName']})


def wirte():
    while 1:
        dic = q.get()
        pid = dic['pid']
        app = dic['app']
        w.writerow([pid, app])
        f.flush()
        print(pid)


if __name__ == "__main__":
    Thread(target=wirte, args=()).start()
    i = 1
    while i:
        semaphore.acquire()
        Thread(target=collectapp, args=(i,)).start()
        i += 1
