# -*- encoding: utf-8 -*-
__author__ = 'faide'

import os
import unittest
import zipfile
import traceback

import lxml.etree
import pkg_resources

from io import BytesIO

from genshi.template import TemplateError

from nose.tools import raises

from pyjon.utils import get_secure_filename

from py3o.template.main import Template, TemplateException, XML_NS


class TestTemplate(unittest.TestCase):

    def tearDown(self):
        pass

    def setUp(self):
        pass

    def test_example_1(self):
        template_name = pkg_resources.resource_filename(
            'py3o.template',
            'tests/templates/py3o_example_template.odt'
        )

        outname = get_secure_filename()

        template = Template(template_name, outname)
        template.set_image_path('logo', pkg_resources.resource_filename(
            'py3o.template',
            'tests/templates/images/new_logo.png'
        ))

        class Item(object):
            pass

        items = list()

        item1 = Item()
        item1.val1 = 'Item1 Value1'
        item1.val2 = 'Item1 Value2'
        item1.val3 = 'Item1 Value3'
        item1.Currency = 'EUR'
        item1.Amount = '12345.35'
        item1.InvoiceRef = '#1234'
        items.append(item1)

        # if you are using python 2.x you should use xrange
        for i in range(1000):
            item = Item()
            item.val1 = 'Item%s Value1' % i
            item.val2 = 'Item%s Value2' % i
            item.val3 = 'Item%s Value3' % i
            item.Currency = 'EUR'
            item.Amount = '6666.77'
            item.InvoiceRef = 'Reference #%04d' % i
            items.append(item)

        document = Item()
        document.total = '9999999999999.999'

        data = dict(items=items, document=document)
        error = False
        try:
            template.render(data)
        except ValueError as e:
            print('The template did not render properly...')
            traceback.print_exc()
            error = True

        assert error is False

    def test_list_duplicate(self):
        """test duplicated listed get a unique id"""
        template_name = pkg_resources.resource_filename(
            'py3o.template',
            'tests/templates/py3o_list_template.odt'
        )
        outname = get_secure_filename()

        template = Template(template_name, outname)

        class Item(object):
            def __init__(self, val):
                self.val = val
        data_dict = {
            "items": [Item(1), Item(2), Item(3), Item(4)]
        }

        error = False

        template.set_image_path('logo', pkg_resources.resource_filename(
            'py3o.template',
            'tests/templates/images/new_logo.png'
        ))
        template.render(data_dict)

        outodt = zipfile.ZipFile(outname, 'r')
        try:
            content_list = [
                lxml.etree.parse(BytesIO(outodt.read(filename)))
                for filename in template.templated_files
            ]
        except lxml.etree.XMLSyntaxError as e:
            error = True
            print(
                "List was not deduplicated->{}".format(e)
            )

        # remove end file
        os.unlink(outname)

        assert error is False

        # first content is the content.xml
        content = content_list[0]
        list_expr = '//text:list'
        list_items = content.xpath(
            list_expr,
            namespaces=template.namespaces
        )
        ids = []
        for list_item in list_items:
            ids.append(
                list_item.get(
                    '{}id'.format(XML_NS)
                )
            )
        assert ids, "this list of ids should not be empty"
        assert len(ids) == len(set(ids)), "all ids should have been unique"

    def test_missing_opening(self):
        """test orphaned /for raises a TemplateException"""
        template_name = pkg_resources.resource_filename(
            'py3o.template',
            'tests/templates/py3o_missing_open_template.odt'
        )
        outname = get_secure_filename()
        try:
            template = Template(template_name, outname)

        finally:
            os.remove(outname)

        class Item(object):
            def __init__(self, val):
                self.val = val
        data_dict = {
            "items": [Item(1), Item(2), Item(3), Item(4)]
        }

        template.set_image_path('logo', pkg_resources.resource_filename(
            'py3o.template',
            'tests/templates/images/new_logo.png'
        ))
        # this will raise a TemplateException... or the test will fail
        error_occured = False
        try:
            template.render(data_dict)

        except TemplateException as e:
            error_occured = True
            # make sure this is the correct TemplateException that pops
            assert e.message == "No open instruction for /for"

        # and make sure we raised
        assert error_occured is True

    def test_ignore_undefined_variables_logo(self):

        template_name = pkg_resources.resource_filename(
            'py3o.template',
            'tests/templates/py3o_logo.odt'
        )

        outname = get_secure_filename()

        template = Template(template_name, outname)

        data = {}

        error = True
        try:
            template.render(data)
            print("Error: template contains a logo variable that must be "
                  "replaced")
        except ValueError:
            error = False

        assert error is False

        template = Template(template_name, outname,
                            ignore_undefined_variables=True)

        error = False
        try:
            template.render(data)
        except:
            traceback.print_exc()
            error = True

        assert error is False

    def test_ignore_undefined_variables_1(self):

        template_name = pkg_resources.resource_filename(
            'py3o.template',
            'tests/templates/py3o_undefined_variables_1.odt'
        )

        outname = get_secure_filename()

        template = Template(template_name, outname)

        data = {}

        error = True
        try:
            template.render(data)
            print("Error: template contains variables that must be "
                  "replaced")
        except TemplateError:
            error = False

        assert error is False

        template = Template(template_name, outname,
                            ignore_undefined_variables=True)

        error = False
        try:
            template.render(data)
        except:
            traceback.print_exc()
            error = True

        assert error is False

    def test_ignore_undefined_variables_2(self):
        """
        Test ignore undefined variables for template with dotted variables like
        py3o.document.value
        """

        template_name = pkg_resources.resource_filename(
            'py3o.template',
            'tests/templates/py3o_undefined_variables_2.odt'
        )

        outname = get_secure_filename()

        template = Template(template_name, outname)

        data = {}

        error = True
        try:
            template.render(data)
            print("Error: template contains variables that must be "
                  "replaced")
        except TemplateError:
            error = False

        assert error is False

        template = Template(template_name, outname,
                            ignore_undefined_variables=True)

        error = True
        try:
            template.render(data)
            print("Error: template contains dotted variables that must be "
                  "replaced")
        except TemplateError:
            error = False

        assert error is False
