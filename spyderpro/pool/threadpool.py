import os
from threading import Thread

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
        self._wait = Queue(max_workers)  # 线程所有任务结束通知
        self._state = False  # 是否执行过一遍任务，避免反复执行
        self.result = list()

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

    def _adjust_thread_count(self):
        """
        监听线程
        """
        while self._stop.get():
            w = self._work_queue.get()  # 获取任务
            response = w.run()  # 执行任务
            self.result.append(response)
        self._wait.put(1)  # 一个线程的所有任务完成了，销毁

    def shut_down(self):
        """
        关闭线程池
        :return:
        """
        self._shutdown = True

    def close_nowait(self):
        """
        终止每个线程，无需阻塞等待所有任务完成

        :return:
        """
        for i in range(self._max_workers):
            self._stop.put(0)  # 通知关闭线程

    def close(self):
        """
        终止每个线程，阻塞等待所有任务完成
        :return:
        """
        for i in range(self._max_workers):
            self._stop.put(0)  # 通知关闭线程
        count = 0
        while 1:
            self._wait.get()
            count += 1
            if count == self._max_workers:
                break
