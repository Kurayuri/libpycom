class MultiKeyDict:
    def __init__(self, *titles):
        self.titles = titles
        self.dicts = {}

        for title in self.titles:
            self.dicts[title] = {}

    def set(self, value, *args, **kwargs):

        if args:
            if len(args) != len(self.titles):
                raise ValueError(f"Required {len(self.titles)} keys，but {len(args)} is provided.")
            keys = list(args)
        elif kwargs:
            if len(kwargs) != len(self.titles):
                raise ValueError(f"Required {len(self.titles)} keys，but {len(kwargs)} is provided. 个。")
            keys = [kwargs[title] for title in self.titles]
        else:
            raise ValueError("No args or kwargs.")

        for title_idx, title in enumerate(self.titles):
            _dict = self.dicts[title]
            _keys = [keys[title_idx]] + keys[:title_idx] + keys[title_idx + 1:]

            for key in _keys[:-1]:
                _dict.setdefault(key, {})
                _dict = _dict[key]
            _dict[_keys[-1]] = value

    def get(self, *args, **kwargs):
        if args:
            if len(args) != len(self.titles):
                raise ValueError(f"Required {len(self.titles)} keys，but {len(args)} is provided.")
            keys = list(args)
        elif kwargs:
            if len(kwargs) != len(self.titles):
                raise ValueError(f"Required {len(self.titles)} keys，but {len(kwargs)} is provided. 个。")
            keys = [kwargs[title] for title in self.titles]
        else:
            raise ValueError("No args or kwargs.")

        for title_idx, title in enumerate(self.titles):
            _dict = self.dicts[title]
            _keys = [keys[title_idx]] + keys[:title_idx] + keys[title_idx + 1:]

            for key in _keys:
                _dict = _dict.get(key)
                if _dict is None:
                    break
            return _dict

    def __str__(self) -> str:
        return f"{self.dicts}"
