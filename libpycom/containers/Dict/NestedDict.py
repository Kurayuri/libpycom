class NestedDict:
    def __init__(self, sep="_"):
        self.sep = sep
        self._dict_by_nested = {}

        self.data_by_combination = {}
        self.data_by_datacenter = {}

    def set_by_keys(self, country, province, isp, datacenter, value):
        """设置值，并更新所有访问方式的字典"""
        # 更新核心嵌套字典结构
        if country not in self._dict_by_nested:
            self._dict_by_nested[country] = {}
        if province not in self._dict_by_nested[country]:
            self._dict_by_nested[country][province] = {}
        if isp not in self._dict_by_nested[country][province]:
            self._dict_by_nested[country][province][isp] = {}

        self._dict_by_nested[country][province][isp][datacenter] = value

        # 生成组合键
        combination_key = self.sep.join([country, province, isp])
        f"{country}_{province}_{isp}"

        # 更新组合键字典
        if combination_key not in self.data_by_combination:
            self.data_by_combination[combination_key] = {}
        self.data_by_combination[combination_key][datacenter] = value

        # 更新机房字典
        if datacenter not in self.data_by_datacenter:
            self.data_by_datacenter[datacenter] = {}
        self.data_by_datacenter[datacenter][combination_key] = value

    def set_by_combination(self, combination_key, datacenter, value):
        self.set_by_keys(*combination_key.split(self.sep), datacenter, value)

    def get_by_nested(self, country, province, isp, datacenter):
        """通过国家、省份、运营商和机房访问数据"""
        return self._dict_by_nested.get(country, {}).get(province, {}).get(isp, {}).get(datacenter)

    def get_by_combination(self, combination_key, datacenter):
        """通过组合键和机房访问数据"""
        return self.data_by_combination.get(combination_key, {}).get(datacenter)

    def get_by_datacenter(self, datacenter, combination_key):
        """通过机房和组合键访问数据"""
        return self.data_by_datacenter.get(datacenter, {}).get(combination_key)


class MultiKeyDict:
    def __init__(self, primary_key_idxs, keys_num: int = None):
        """
        初始化字典，接受多个主键。
        primary_keys: 作为主键的键列表
        """
        self._dict = {}  # 存储所有数据
        self._primary_key_idxs = primary_key_idxs  # 记录哪些键是主键
        self._dict = {key: {} for key in primary_key_idxs}  # 为每个主键建立索引字典
        self._other_key_idxs = None
        if keys_num is not None:
            self._other_key_idxs = self.calc_okey_idx(keys_num)

    def calc_okey_idx(self, keys_num):
        return tuple(i for i in range(keys_num) if i not in self._primary_key_idxs)

    def set(self, value, *args):
        """
        设置数据，kwargs 包含主键及其他属性。
        """
        keys = list(args)

        okey_idxs = self.calc_okey_idx(len(args)) if self._other_key_idxs is None else self._other_key_idxs

        flag_no_okey = (len(okey_idxs) == 0)

        for idx, pkey_idx in enumerate(self._primary_key_idxs):
            keys.pop(pkey_idx)
            left_primary_key_idxs = self._primary_key_idxs[:idx] + self._primary_key_idxs[idx + 1:]

            if flag_no_okey and len(self._primary_key_idxs) == 1:
                self._dict[args[pkey_idx]] = value

            for _pkey_idx in left_primary_key_idxs[:-1]:
                _dict = _dict.setdefault(args[_pkey_idx], {})

            for _pkey_idx in left_primary_key_idxs[-1:]:
                if flag_no_okey:
                    _dict[args[_pkey_idx]] = value
                else:
                    _dict = _dict.setdefault(args[_pkey_idx], {})

            if not flag_no_okey:
                _dict[okey_idxs] = value

    def accessByKey(self, **kwargs):
        """
        通过指定的主键及其值来访问数据。
        kwargs 只需包含主键及其对应的值。
        """
        if not kwargs:
            return self._dict  # 如果没有提供主键，返回所有数据

        # 确保传入的键是主键
        for key in kwargs:
            if key not in self._primary_key_idxs:
                raise KeyError(f"{key} is not a primary key")

        # 使用第一个提供的主键查找索引
        key_name, key_value = next(iter(kwargs.items()))
        if key_name in self._dict and key_value in self._dict[key_name]:
            index_subset = self._dict[key_name][key_value]
            # 检查其他主键的值是否匹配
            for key, value in kwargs.items():
                index_subset = {k: v for k, v in index_subset.items() if k[self._key_order(key)] == value}
            return {k: self._dict[k] for k in index_subset.keys()}

        raise KeyError(f"No matching data for key combination: {kwargs}")

    def delete(self, **kwargs):
        """
        删除指定的主键对应的数据。
        kwargs 需要包含所有的主键及其对应的值。
        """
        # 构建组合键
        key_tuple = tuple(kwargs[key] for key in self._primary_key_idxs)
        if key_tuple in self._dict:
            # 删除数据
            del self._dict[key_tuple]
            # 同步删除各主键的索引
            for key in self._primary_key_idxs:
                key_value = kwargs[key]
                if key_value in self._dict[key]:
                    del self._dict[key][key_value][key_tuple]
                    if not self._dict[key][key_value]:
                        del self._dict[key][key_value]
        else:
            raise KeyError(f"No data found for key combination: {kwargs}")

    def _key_order(self, key):
        """
        返回主键在定义时的顺序索引。
        """
        return self._primary_key_idxs.index(key)
