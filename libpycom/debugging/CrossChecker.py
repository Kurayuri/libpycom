from types import EllipsisType
from typing import Any
from libpycom import Messager
from libpycom.Settings import Settings
from matplotlib.pyplot import style
import zmq
import os


class CrossChecker:
    def __init__(self, checker_name: str | EllipsisType = ..., ip="localhost", port=5555, messager: Messager | EllipsisType = ...):
        if messager is ...:
            messager = Settings.messager
        self.messager = messager
        self.checker_name = checker_name if checker_name is not ... else str(os.getpid())
        self.ip = ip
        self.port = port
        self.address = f"tcp://{self.ip}:{self.port}"
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUSH)
        self.socket.connect(self.address)

        self.index = 0

    def check(self, value: Any, id=None):
        value = str(value)
        data = {
            "src": self.checker_name,
            "idx": self.index,
            "id": id,
            "val": value,
        }
        self.socket.send_json(data)
        self.index += 1

    def close(self):
        self.socket.close()
        self.context.term()

    def __del__(self):
        self.close()


_checker = CrossChecker(str(os.getpid()), messager=Settings.messager)
check = _checker.check


class CrossMonitor:
    def __init__(self, n_checkers=None, ip="localhost", port=5555, messager: Messager | EllipsisType = ...):
        if messager is ...:
            messager = Settings.messager
        self.messager = messager
        self.ip = ip
        self.port = port
        self.address = f"tcp://{self.ip}:{self.port}"
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PULL)
        self.socket.bind(self.address)
        self.n_checkers = n_checkers

        self.values = {}

    def run(self):
        try:
            while True:
                message = self.socket.recv_json()
                checker_name = message["src"]
                index = message["idx"]
                id = message["id"]
                id = id if id is not None else index
                value = message["val"]

                if checker_name not in self.values:
                    self.values[checker_name] = {}
                self.values.setdefault(id, {})

                if checker_name in self.values[id]:
                    if self.values[id][checker_name] != value:
                        print(f"Duplicated detected: {checker_name} sent {value} but {self.values[id][checker_name]} exists")
                else:
                    self.values[id][checker_name] = value

                pass_flag = True
                for k, v in self.values[id].items():
                    if k == checker_name:
                        continue
                    if value != v:
                        if len(value) > 20:
                            value = value[:20] + "..."
                        if len(v) > 20:
                            v = v[:20] + "..."
                        self.messager.warning(f"Warn {id}: {k} sent {v} and {checker_name} sent {value}", style=Messager.STYLE.RED)
                        pass_flag = False

                if self.n_checkers is not None:
                    if len(self.values[id]) == self.n_checkers and pass_flag:
                        self.messager.info(f"Pass {id}", style=Messager.STYLE.GREEN)
        except KeyboardInterrupt:
            print("Program interrupted by user.")
        finally:
            self.close()

    def close(self):
        self.socket.close()
        self.context.term()

    def __del__(self):
        self.close()
