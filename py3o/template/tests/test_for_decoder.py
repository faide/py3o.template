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

    def test_callable_enumerate_for_iter(self):
        """ Test when iter is a callable
        """
        self.d.decode("for i, j in enumerate(list): pass\n")
        its = self.d.get_iterables()
        assert str(its) == 'list'

    def test_callable_enumerate_for_iter_with_attr(self):
        """ Test when iter is enumerate with attrs as arguments
        """
        self.d.decode("for i, j in enumerate(object.mylist): pass\n")
        its = self.d.get_iterables()
        assert str(its) == 'object.mylist'

    def test_for_dot_attribute(self):
        """ Test when iter is a callable from a dotted expression
        """
        self.d.decode("for i in test.myattr.other_attr: pass\n")
        its = self.d.get_iterables()
        assert str(its) == 'test.myattr.other_attr'

