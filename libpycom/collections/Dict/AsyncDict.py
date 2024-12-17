import multiprocessing as mp
import threading
import time
from typing import Any, Callable

from libpycom.io import open_PathLike
from libpycom.types import PathLike
import orjson

from libpycom.collections.Dict.DictWrapper import DictWrapper


class AsyncDict(DictWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lock = threading.Lock()

    def _load(self, queue, f, callback=None):
        with open_PathLike(f, 'r') as f:
            for idx, line in enumerate(f):
                item = orjson.loads(line)
                item = callback(item) if callback else item
                queue.put(item)
        queue.put(None)

    def _merge(self, queue, init_key, init_line, inited, done):
        idx = 0
        while True:
            item = queue.get()
            idx += 1
            if item is None:
                break
            with self.lock:
                self._dict.update(item)
                if init_key in item or (init_line is not None and idx == init_line):
                    inited.set()
        inited.set()
        done.set()

    def load(self, f: PathLike, init_key: Any | None = None, init_line: int | None = None, callback: Callable | None = None):
        inited = threading.Event()
        done = threading.Event()

        queue = mp.Queue()
        # pool = multiprocessing.Pool(1)

        load_process = mp.Process(target=self._load, args=(queue, f, callback))
        load_process.start()
        # pool.apply(self._load, args=(queue, f, callback))

        merge_thread = threading.Thread(target=self._merge, args=(queue, init_key, init_line, inited, done))
        merge_thread.start()

        inited.wait()

        return done


if __name__ == '__main__':
    ad = AsyncDict()
    dones = []
    for i in range(10):
        done = ad.load("data.jsonl", init_line=1)
        dones.append(done)
        
    while all(not done.is_set() for done in dones):
        time.sleep(0.1)
