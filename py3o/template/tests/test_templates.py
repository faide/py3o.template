__author__ = 'faide'

import unittest
from py3o.template.main import move_siblings
from py3o.template.main import Template
import lxml.etree
import pkg_resources
from pyjon.utils import get_secure_filename
import zipfile
from io import BytesIO
import os
from lxml.etree import XMLSyntaxError


class TestTemplate(unittest.TestCase):

    def tearDown(self):
        pass

    def setUp(self):
        pass

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
            content_trees = [
                lxml.etree.parse(BytesIO(outodt.read(filename)))
                for filename in template.templated_files
            ]
        except XMLSyntaxError as e:
            error = True
            print(
                "List is were not deduplicated->{}".format(e)
            )

        # remove end file
        os.unlink(outname)
        assert error is False
