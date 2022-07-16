from unittest import TestCase
import jsons
from jsons._common_impl import get_class_name, get_cls_from_str, StateHolder


class TestCommonImpl(TestCase):
    def test_get_class_name_without__name__(self):


        class Meta(type):
            __name__ = None

        class C(metaclass=Meta):
            pass

        self.assertEqual('C', get_class_name(C))
        self.assertEqual(f'{__name__}.C', get_class_name(C, fully_qualified=True))

    def test_get_class_name_of_none(self):
        self.assertEqual('NoneType', get_class_name(None))

    def test_get_cls_from_str(self):
        self.assertEqual(str, get_cls_from_str('str', {}, None))
        self.assertEqual(int, get_cls_from_str('int', {}, None))
        self.assertEqual(list, get_cls_from_str('list', {}, None))
