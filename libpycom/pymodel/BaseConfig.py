import os

from libpycom.SyntaxUtils import SyntaxUtils


class BaseConfig:
    def __init__(self):
        # self.init_dir()
        self.create_dirpaths()
        self.Dirpath=0

    def init_dir(self):
        for attr_name in dir(self):
            if attr_name.startswith('dirpath_'):
                dirpath = getattr(self, attr_name)
                os.makedirs(dirpath, exist_ok=True)

    def create_dirpaths(self):
        # 遍历 Dirpath 下的所有子类
        for attr_name in SyntaxUtils.Class.getAttrs(self.Dirpath):
            attr = getattr(self.Dirpath, attr_name)
            if isinstance(attr, type):  # 检查是否为类
                # 遍历子类中的所有路径
                for sub_attr_name in SyntaxUtils.Class.getAttrs(attr):
                    sub_attr = getattr(attr, sub_attr_name)
                    if isinstance(sub_attr, str):  # 确保它是一个字符串路径
                        os.makedirs(sub_attr, exist_ok=True)
