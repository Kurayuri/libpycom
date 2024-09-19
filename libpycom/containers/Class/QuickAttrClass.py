class QuickAttrClass:
    '''
    qac = QuickAttrClass([('a', 'b'), ('c', 'd')]) + QuickAttrClass(
        [('i',), ('j', 'k'), ('l', 'm')], pattern='{}_u{}_v{}')
    qac.a.c = "a_c"
    qac.i.k.m = "i_uk_vm"
    '''

    def __init__(self, attr_sets=None, separator="_", pattern=None):
        if not attr_sets:
            return
        self.__annotations__ = {}  # 初始化 __annotations__ 字典

        for key in attr_sets[0]:
            sub_type = self._create(attr_sets[1:], [key], separator, pattern)
            setattr(self, key, sub_type)
            self.__annotations__[key] = sub_type

    def _create(self, attr_sets, prefix, separator, pattern):
        keys = attr_sets[0]
        attributess = attr_sets[1:]
        sub_attr = {}
        for key in keys:
            if len(attributess) == 0:
                sub_attr[key] = separator.join(prefix+[key]) if pattern is None \
                    else pattern.format(*prefix, key)
            else:
                sub_attr[key] = self._create(
                    attributess, prefix+[key], separator, pattern)
        return type(f'Gen_{prefix}', (object,), sub_attr)

    def update(self, other):
        for key in QuickAttrClass.getAttrs(other):
            if hasattr(self, key):
                self._update_attrs(getattr(self, key), getattr(other, key))
            else:
                setattr(self, key, getattr(other, key))

    def _update_attrs(self, current, other):
        for key in QuickAttrClass.getAttrs(other):
            if hasattr(current, key):
                if isinstance(getattr(current, key), object) and isinstance(getattr(other, key), object):
                    self._update_attrs(
                        getattr(current, key), getattr(other, key))
            else:
                setattr(current, key, getattr(other, key))

    def format(self, pattern):
        def _format_attr(attr):
            if isinstance(attr, str):
                return pattern.format(attr)
            elif isinstance(attr, object) and hasattr(attr, '__dict__'):
                new_sub_attr = {}
                for sub_key, sub_value in attr.__dict__.items():
                    new_sub_attr[sub_key] = _format_attr(sub_value)
                return type(attr.__class__.__name__, (object,), new_sub_attr)()
            else:
                return attr

        new_qac = QuickAttrClass()
        for key, value in QuickAttrClass.getAttrs(self).items():
            formatted_value = _format_attr(value)
            setattr(new_qac, key, formatted_value)

        return new_qac

    def __add__(self, other):
        result = QuickAttrClass()
        result.update(self)
        result.update(other)
        return result

    @staticmethod
    def getAttrs(obj):
        return {key: value for key, value in obj.__dict__.items()
                if not key.startswith('__') and not key.endswith('__')}


if __name__ == '__main__':
    qac = QuickAttrClass([('a', 'b'), ('c', 'd')]) + QuickAttrClass(
        [('a',), ('j', 'k'), ('l', 'm')], pattern='{}_u{}_v{}')
    assert qac.a.c == "a_c"
    assert qac.a.k.m == "a_uk_vm"
    new_qac = qac.format("@{}@")
    assert new_qac.a.c == "@a_c@"
