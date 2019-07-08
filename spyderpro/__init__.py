import threading, time
import requests
from queue import Queue

import random


class Stu:
    def f(self):
        time.sleep(2+random.randint(3))

        return iter([i for i in range(10000)])


class MyThread(threading.Thread):
    def __init__(self, func, args=()):
        threading.Thread.__init__(self)
        self.func = func
        self.arg = args

    def run(self):
        self.d = self.func()

        semaphore.release()

    def result(self):
        return self.d


def write():
    while True:
        print("start")
        data =q.get()
        print("get")
        for i in data:
            pass
        print("ok")


import  queue

if __name__ == "__main__":
    functionsa = Stu().f
    semaphore = threading.Semaphore(2)  # 每次最多5个线程在执行
    q = queue.Queue(maxsize=5)

    MyThread(write,args=()).start()
    for i in range(1000):
        semaphore.acquire()
        t = MyThread(functionsa, args=())
        t.start()


