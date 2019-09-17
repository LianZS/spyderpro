import os
from threading import Thread, Lock, Semaphore

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
        self._max_workers = Semaphore(max_workers)
        self._work_queue = Queue(max_workers)  # 存放任务
        self._broken = False
        self._shutdown = False
        self._shutdown_lock = Lock()

    def submit(self, fn, *args, **kwargs):
        if self._shutdown:
            raise RuntimeError('线程池已经关闭，无法创建新的线程')
        w = _Worker(fn, args, kwargs)
        self._work_queue.put(w)  # 任务队列

        self._max_workers.acquire()

        Thread(target=self._adjust_thread_count, args=()).start()

    def _adjust_thread_count(self):
        w = self._work_queue.get()
        w.run()
        self._max_workers.release()

    def shut_down(self):
        """
        关闭线程池
        :return:
        """
        self._shutdown = True


def test(i):
    print(i)
    time.sleep(1)


if __name__ == "__main__":
    import time

    pool = ThreadPool(max_workers=5)
    for k in range(14):
        pool.sumbit(test, k)
