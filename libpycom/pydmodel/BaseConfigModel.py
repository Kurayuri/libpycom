import builtins
import os
from pathlib import Path

import yaml
from pydantic import BaseModel, model_validator

from libpycom.collections.Dict.DotDict import DotDict
from libpycom.SyntaxUtils import SyntaxUtils

CONFIG_GLOBAL_VARS: DotDict


class BaseModelConfig(BaseModel):
    @classmethod
    def load(cls, filepath: str = None):
        # if filepath is None:
        #     filepath = pkg_resources.resource_filename("bridge", 'config.yaml')
        with open(filepath, 'r') as file:
            config_data = yaml.safe_load(file)
        config = cls(**config_data)
        return config

    @model_validator(mode='before')
    def __add_CONFIG_GLOBAL_VARS(cls, values):
        vars = {}
        for field_name, field_value in values.items():
            if not isinstance(field_value, BaseModel):
                vars[field_name] = field_value
        builtins.CONFIG_GLOBAL_VARS = vars
        return values


class BaseModelPath(BaseModel):
    __Basepath__: str = "."
    __BasepathSrc__: str | None = None
    __MakeDir__: bool = False

    @model_validator(mode='after')
    def __join_basepath(self):
        if self.__BasepathSrc__ is not None:
            self.__Basepath__ = CONFIG_GLOBAL_VARS[self.__BasepathSrc__]
        for k, v in self.__dict__.items():
            # k_type = self.__annotations__.get(k)
            if isinstance(v, Path):
                _v = self.__Basepath__ / v
                setattr(self, k, _v)
                if self.__MakeDir__:
                    os.makedirs(_v, exist_ok=True)

        return self


class BaseModelFString(BaseModel):
    @model_validator(mode='after')
    def __format_str(self):
        for k, v in self.__dict__.items():
            k_type = self.__annotations__.get(k)
            if k_type is str:
                _v = SyntaxUtils.Str.formatFString(v, CONFIG_GLOBAL_VARS)
                setattr(self, k, _v)

        return self
