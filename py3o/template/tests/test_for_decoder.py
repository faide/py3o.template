__author__ = 'alorimier'

import unittest
from py3o.template.decoder import Decoder


class TestDecoder(unittest.TestCase):
    def setUp(self):
        self.d = Decoder()

    def test_for_not_implemented(self):
        """test if exception is raised correctly"""
        error = False
        try:
            self.d.decode("if i == 0: pass\n")
        except NotImplementedError:
            error = False
        assert error is False

    def test_simple_for_variables(self):
        """ Test a simple for loop vars
        """
        self.d.decode("for i in toto: pass\n")
        v = self.d.get_variables()
        assert v == 'i'

    def test_tuple_for_variable(self):
        """ Test when a tuple is defined in the for loop
        """
        self.d.decode("for i, j in toto: pass\n")
        v = self.d.get_variables()
        assert v == ('i', 'j')

    def test_simple_for_iter(self):
        """ Test a simple for loop iter
        """
        self.d.decode("for i in toto: pass\n")
        its = self.d.get_iterables()
        assert its == 'toto'

    def test_simple_callable_for_iter(self):
        """ Test when iter is a callable
        """
        self.d.decode("for i, j in enumerate(list): pass\n")
        its = self.d.get_iterables()
        assert its.get_func_str() == 'enumerate(list)'

    def test_callable_w_kwargs_for_iter(self):
        """ Test when iter is a callable with keywords arguments
        """
        self.d.decode("for i, j in func(arg1, kwarg1=some_values): pass\n")
        its = self.d.get_iterables()
        assert its.get_func_str() == 'func(arg1, kwarg1=some_values)'

    def test_for_dot_attribute(self):
        """ Test when iter is a callable from a dotted expression
        """
        self.d.decode("for i in test.myattr.other_attr: pass\n")
        its = self.d.get_iterables()
        str = its.get_attr_str()
        assert str == 'test.myattr.other_attr'

