import json
from mock import Mock

__author__ = 'alorimier'

import unittest
from py3o.template.decoder import Decoder, ForList
import pkg_resources
from py3o.template import Template
from pyjon.utils import get_secure_filename


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
        res = self.d.decode("for i in toto: pass\n")
        assert res[0] == 'i'

    def test_tuple_for_variable(self):
        """ Test when a tuple is defined in the for loop
        """
        res = self.d.decode("for i, j in toto: pass\n")
        assert res[0] == ('i', 'j')

    def test_simple_for_iter(self):
        """ Test a simple for loop iter
        """
        res = self.d.decode("for i in toto: pass\n")
        assert res[1] == 'toto'

    def test_callable_enumerate_for_iter(self):
        """ Test when iter is a callable
        """
        res = self.d.decode("for i, j in enumerate(list): pass\n")
        assert str(res[1]) == 'list'

    def test_callable_enumerate_for_iter_with_attr(self):
        """ Test when iter is enumerate with attrs as arguments
        """
        res = self.d.decode("for i, j in enumerate(object.mylist): pass\n")
        assert str(res[1]) == 'object.mylist'

    def test_for_dot_attribute(self):
        """ Test when iter is a callable from a dotted expression
        """
        res = self.d.decode("for i in test.myattr.other_attr: pass\n")
        assert str(res[1]) == 'test.myattr.other_attr'

    def test_jsonify_empty_for_loop(self):
        """ Test the jsonify function
        """
        template_xml = pkg_resources.resource_filename(
            'py3o.template',
            'tests/templates/py3o_empty_for_loop.odt'
        )
        t = Template(template_xml, get_secure_filename())
        for_lists, variables = t.get_user_instructions_mapping()
        data = {
            'my1list': []
        }
        res = ForList.to_dict(for_lists, variables, data)
        expected = {'my1list': []}
        assert res == expected

    def test_jsonify_access_in_loop_variable(self):
        """ Test the jsonify function
        """
        template_xml = pkg_resources.resource_filename(
            'py3o.template',
            'tests/templates/py3o_access_in_loop_variable.odt'
        )
        t = Template(template_xml, get_secure_filename())
        for_lists, variables = t.get_user_instructions_mapping()
        data = {
            'my2list': ['val1', 'val2']
        }
        res = ForList.to_dict(for_lists, variables, data)
        expected = {'my2list': ['val1', 'val2']}
        assert res == expected

    def test_jsonify_in_loop_variable_with_attribute(self):
        """ Test the jsonify function
        """
        template_xml = pkg_resources.resource_filename(
            'py3o.template',
            'tests/templates/py3o_access_in_loop_variable_with_attribute.odt'
        )
        t = Template(template_xml, get_secure_filename())
        for_lists, variables = t.get_user_instructions_mapping()
        data = {
            'my3list': [Mock(val='val1'), Mock(val='val2')]
        }
        res = ForList.to_dict(for_lists, variables, data)
        expected = {'my3list': [{'val': 'val1'}, {'val': 'val2'}]}
        assert res == expected

    def test_jsonify_global_variable_inside_loop(self):
        """ Test the jsonify function
        """
        template_xml = pkg_resources.resource_filename(
            'py3o.template',
            'tests/templates/py3o_access_global_variable_inside_loop.odt'
        )
        t = Template(template_xml, get_secure_filename())
        for_lists, variables = t.get_user_instructions_mapping()
        data = {
            'global_var': Mock(val='global_val')
        }
        res = ForList.to_dict(for_lists, variables, data)
        expected = {'global_var': {'val': 'global_val'}, 'my4list': []}
        assert res == expected

    def test_jsonify_iterator_with_attribute(self):
        """ Test the jsonify function
        """
        template_xml = pkg_resources.resource_filename(
            'py3o.template',
            'tests/templates/py3o_iterator_with_attribute.odt'
        )
        t = Template(template_xml, get_secure_filename())
        for_lists, variables = t.get_user_instructions_mapping()
        data = {
            'global_var': Mock(my5list=[])
        }
        res = ForList.to_dict(for_lists, variables, data)
        expected = {'global_var': {'my5list': []}}
        assert res == expected

    def test_jsonify_iterator_with_attribute_and_in_loop_variable(self):
        """ Test the jsonify function
        """
        template_xml = pkg_resources.resource_filename(
            'py3o.template',
            'tests/templates/py3o_iterator_with_attribute_and_in_loop_variable.odt'
        )
        t = Template(template_xml, get_secure_filename())
        for_lists, variables = t.get_user_instructions_mapping()
        data = {
            'global_var': Mock(my6list=['val1', 'val2'])
        }
        res = ForList.to_dict(for_lists, variables, data)
        expected = {'global_var': {'my6list': ['val1', 'val2']}}
        assert res == expected

    def test_jsonify_iterator_with_attribute_and_in_loop_variable_with_attribute(self):
        """ Test the jsonify function
        """
        template_xml = pkg_resources.resource_filename(
            'py3o.template',
            'tests/templates/py3o_iterator_with_attribute_and_in_loop_variable_with_attribute.odt'
        )
        t = Template(template_xml, get_secure_filename())
        for_lists, variables = t.get_user_instructions_mapping()
        data = {
            'global_var': Mock(my7list=[Mock(val='val1'), Mock(val='val2')])
        }
        res = ForList.to_dict(for_lists, variables, data)
        expected = {'global_var': {'my7list': [{'val': 'val1'}, {'val': 'val2'}]}}
        assert res == expected

#    def test_jsonify_access_variable_in_nested_loop(self):
#        """ Test the jsonify function
#        """
#        template_xml = pkg_resources.resource_filename(
#            'py3o.template',
#            'tests/templates/py3o_access_variable_in_nested_loop.odt'
#        )
#        t = Template(template_xml, get_secure_filename())
#        for_lists, variables = t.get_user_instructions_mapping()
#        data = {
#            'my8list': [['val1', 'val2'], ['val3']]
#        }
#        res = ForList.to_dict(for_lists, variables, data)
#        expected = {'my8list': [['val1', 'val2'], ['val3']]}
#        assert res == expected

#    def test_jsonify_access_parent_variable_in_nested_loop(self):
#        """ Test the jsonify function
#        """
#        template_xml = pkg_resources.resource_filename(
#            'py3o.template',
#            'tests/templates/py3o_access_parent_variable_in_nested_loop.odt'
#        )
#        t = Template(template_xml, get_secure_filename())
#        for_lists, variables = t.get_user_instructions_mapping()
#        data = {
#            'my9list': [Mock(val='val1', mylist=[]), Mock(val='val2', mylist=[])]
#        }
#        res = ForList.jsonify(for_lists, variables, data)
#        expected = "{'my9list': [{'val': 'val1', 'mylist': []}, {'val': 'val2', 'mylist': []}]}"
#        assert res == expected
#
#    def test_jsonify_access_variable_in_nested_loop_with_attribute(self):
#        """ Test the jsonify function
#        """
#        template_xml = pkg_resources.resource_filename(
#            'py3o.template',
#            'tests/templates/py3o_access_variable_in_nested_loop_with_attribute.odt'
#        )
#        t = Template(template_xml, get_secure_filename())
#        for_lists, variables = t.get_user_instructions_mapping()
#        data = {
#            'my10list': [Mock(my_list=[Mock(val='val1'), Mock(val='val2')]), Mock(my_list=[Mock(val='val3')])]
#        }
#        res = ForList.jsonify(for_lists, variables, data)
#        expected = "{'my10list': [{'my_list': [{'val': 'val1'}, {'val': 'val2'}]}, {'my_list': [{'val': 'val3'}]}]}"
#        assert res == expected