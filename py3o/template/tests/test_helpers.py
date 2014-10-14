__author__ = 'faide'

import unittest
from py3o.template.main import move_siblings
import lxml.etree
import pkg_resources
from io import BytesIO


class TestMoveSiblings(unittest.TestCase):

    def tearDown(self):
        pass

    def setUp(self):
        pass

    def test_move_1(self):
        """test that siblings are properly moved"""
        template_one_name = pkg_resources.resource_filename(
            'py3o.template',
            'tests/templates/move_one.xml'
        )
        test_template_one = lxml.etree.parse(
            BytesIO(open(template_one_name).read())
        )
        start = test_template_one.find('mystruct/start')
        end = test_template_one.find('mystruct/end')
        new_ = test_template_one.find('mystruct/finishcontainer')

        move_siblings(start, end, new_)

        result_s = lxml.etree.tostring(
            test_template_one,
            pretty_print=True,
        )

        expected_result = open(
            pkg_resources.resource_filename(
                'py3o.template',
                'tests/templates/move_one_result.xml'
            )
        ).read()

        assert result_s == expected_result

    def test_move_2(self):
        """test that start.tail is correctly copied"""
        template_two_name = pkg_resources.resource_filename(
            'py3o.template',
            'tests/templates/move_two.xml'
        )
        test_template_two = lxml.etree.parse(
            BytesIO(open(template_two_name).read())
        )
        start = test_template_two.find('mystruct/start')
        end = test_template_two.find('mystruct/end')
        new_ = test_template_two.find('mystruct/finishcontainer')

        move_siblings(start, end, new_)

        result_s = lxml.etree.tostring(
            test_template_two,
            pretty_print=True,
        )

        expected_result = open(
            pkg_resources.resource_filename(
                'py3o.template',
                'tests/templates/move_two_result.xml'
            )
        ).read()

        print(result_s)

        assert result_s == expected_result
