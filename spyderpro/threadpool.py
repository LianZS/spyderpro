import os
from threading import Thread, Lock, Semaphore

from queue import Queue


allow_add_task = Semaphore(5)


class _Worker(object):
    def __init__(self, fn, args, kwargs):
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def run(self):

        try:
            result = self.fn(*self.args, **self.kwargs)
            allow_add_task.release()

        except Exception as e:
            result = None
        return result


class ThreadPool():
    def __init__(self, max_workers=None):
        if max_workers is None:
            max_workers = (os.cpu_count() or 1) * 5
        if max_workers <= 0:
            raise ValueError("最大线程数必须大于0")
        self._max_workers = max_workers
        self._work_queue = Queue(max_workers)  # 存放任务
        self._broken = False
        self._shutdown = False
        self._shutdown_lock = Lock()

    def sumbit(self, fn, *args, **kwargs):
        if self._shutdown:
            raise RuntimeError('线程池已经关闭，无法创建新的线程')
        w = _Worker(fn, args, kwargs)
        self._work_queue.put(w)
        self._adjust_thread_count()

    def _adjust_thread_count(self):
        allow_add_task.acquire()
        w = self._work_queue.get()
        t = Thread(target=w.run)
        t.start()


