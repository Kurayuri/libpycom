import pytest
from libpycom.metatypes import Sentinel, ValueEnum


def test_sentinel_creation():
    sentinel1 = Sentinel('TEST')
    sentinel2 = Sentinel('TEST')
    assert sentinel1 is sentinel2
    assert repr(sentinel1) == '<TEST>'
    assert bool(sentinel1)


def test_sentinel_custom_repr():
    sentinel = Sentinel('TEST_CUSTOM', repr='CustomRepr')
    assert repr(sentinel) == 'CustomRepr'


def test_sentinel_bool_value():
    sentinel_true = Sentinel('TEST_TRUE', bool_value=True)
    sentinel_false = Sentinel('TEST_FALSE', bool_value=False)
    assert bool(sentinel_true)
    assert not bool(sentinel_false)


def test_sentinel_module_name():
    sentinel = Sentinel('TEST_MODULE')
    assert sentinel._module_name == 'test_metatypes'


def test_value_enum():
    class TestValueEnumA(ValueEnum):
        A = 1
        B = 2

    assert len(TestValueEnumA) == 2
    assert TestValueEnumA.A in TestValueEnumA
    assert TestValueEnumA.B in TestValueEnumA
    assert TestValueEnumA.A == 1
    assert TestValueEnumA.B == 2
    with pytest.raises(AttributeError):
        _ = TestValueEnumA.C

    class TestValueEnumB(ValueEnum):
        X = 10
        Y = 20

    assert len(TestValueEnumB) == 2
    assert TestValueEnumB.X in TestValueEnumB
    assert TestValueEnumB.Y in TestValueEnumB
    assert TestValueEnumB.X == 10
    assert TestValueEnumB.Y == 20


def test_value_enum_iteration():
    class TestValueEnumC(ValueEnum):
        A = 1
        B = 2
        C = 3

    values = list(TestValueEnumC)
    assert len(values) == 3
    assert TestValueEnumC.A in values
    assert TestValueEnumC.B in values
    assert TestValueEnumC.C in values
    assert values == [1, 2, 3]


if __name__ == '__main__':
    pytest.main()
