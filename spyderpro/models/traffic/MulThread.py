from threading import Thread


class MulitThread(Thread):
    def __init__(self, target, args=()):
        Thread.__init__(self)
        self.func = target
        self.args = args

    def run(self):
        self.result = self.func(*self.args)

    @property
    def get_result(self):
        return self.result
