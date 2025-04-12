import os
from pathlib import Path
from libpycom.types import PostProcClass

def join_path(basedir):
    def post_proc(x):
        if isinstance(x, str):
            return os.path.join(basedir, x)
        elif isinstance(x, Path):
            return Path(basedir) / x
        elif isinstance(x, list):
            return [os.path.join(basedir, i) for i in x]
        else:
            return x
    return post_proc


'''
basedir = '...'
class Path(File, PostProcClass, post_proc=partial(post_proc, basedir=basedir)):
    ...
'''
