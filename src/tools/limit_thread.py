# -*- coding:utf-8 -*-
# @Time        : 2022/1/5 17:51
# @Author      : Tuffy
# @Description :
import ctypes
import threading

from .exceptions import ThreadNotAliveException


class LimitThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, *, daemon=True):
        super().__init__(group, name=name, daemon=daemon)
        self.target = target
        self.args = args
        self.kwargs = kwargs if kwargs else {}
        self.result = None

    def run(self):
        try:
            self.result = self.target(*self.args, **self.kwargs)
        except Exception as exc:
            print(exc)

    def stop(self):
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(self.ident, ctypes.py_object(SystemExit))
        if res == 0:
            raise ThreadNotAliveException("Thread not alive")
        elif res != 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(self.ident, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")

    def wait_result(self, timeout):
        self.join(timeout)
        try:
            self.stop()
        except Exception as exc:
            print(exc)
        return self.result if self.result else None
