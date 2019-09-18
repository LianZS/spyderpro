import os
from threading import Thread, Event, Lock

from queue import Queue


class _Worker(object):
    def __init__(self, fn, args, kwargs):
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def run(self):

        try:
            result = self.fn(*self.args, **self.kwargs)

        except Exception  as e:
            print(e)
            result = None
        return result


class ThreadPool():

    def __init__(self, max_workers=None):
        if max_workers is None:
            max_workers = (os.cpu_count() or 1) * 5
        if max_workers <= 0:
            raise ValueError("最大线程数必须大于0")
        self._max_workers = max_workers  # 最大线程数
        self._work_queue = Queue(max_workers)  # 任务队列
        self._work_list = list()  # 任务列表
        self._stop = Queue(max_workers)  # 线程是否关闭消息队列
        self._shutdown = False  # 是否关闭线程池
        self._thread_list = list()  # 线程列表

        self._create_thread()  # 初始化线程池
        self._state = False  # 是否执行过一遍任务，避免反复执行

    def _create_thread(self):
        """
        创建线程池
        :return:
        """
        for i in range(self._max_workers):
            t = Thread(target=self._adjust_thread_count, args=())
            self._thread_list.append(t)
            t.start()

    def submit(self, fn, *args, **kwargs):
        """
        提交任务
        :param fn:
        :param args:
        :param kwargs:
        :return:
        """
        if self._shutdown:
            raise RuntimeError('线程池已经关闭，无法创建新的线程')
        self._state = False
        w = _Worker(fn, args, kwargs)
        self._work_list.append(w)

    def run(self):
        """
        启动任务
        :return:
        """
        if self._state:
            raise BaseException("任务已经过一遍，不可重复执行")
        for w in self._work_list:
            self._stop.put(1)
            self._work_queue.put(w)
        self._state = True  # 设置该任务集已经执行过一遍了
        self._work_list.clear()
        # self.close()

    def _adjust_thread_count(self):
        """
        监听线程
        """
        while self._stop.get():
            w = self._work_queue.get()  # 获取任务
            w.run()  # 执行任务

    def shut_down(self):
        """
        关闭线程池
        :return:
        """
        self._shutdown = True

    def close(self):
        """
        终止每个线程
        :return:
        """
        for i in range(self._max_workers):
            self._stop.put(0)  # 通知关闭线程


def test(i):
    print(i)
    time.sleep(1)


if __name__ == "__main__":
    import time

    pool = ThreadPool(max_workers=5)
    for k in range(14):
        pool.submit(test, k)
    pool.run()
    pool.submit(test,100)
    pool.run()
    pool.close()
