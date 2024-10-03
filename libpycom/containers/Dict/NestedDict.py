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

