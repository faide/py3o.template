Introduction
============

py3o is an elegant and scalable solution to design
reports using LibreOffice or OpenOffice.
py3o.template is the templating component that takes care of
merging your datasets with a corresponding templated OpenOffice document.

It is plateform independant and does not require LibreOffice/OpenOffice itself
to generate an ODF file.
If you want to generate a PDF or any other support output format you will then
need to have a server with either LibreOffice or OpenOffice and to install
the `py3o.renderserver`_ on it.

  .. _py3o.renderserver: https://bitbucket.org/faide/py3o.renderserver/

Full Documentation
==================

We `provide a documentation`_ for this package. If anything is not correctly explained, please! create a ticket `in our ticketing system`_

  .. _provide a documentation: http://py3otemplate.readthedocs.org
  .. _in our ticketing system: https://bitbucket.org/faide/py3o.template/issues?status=new&status=open

Example Usage
=============

Below is an example that you can find in the source tarball inside the examples
directory.

::

    from py3o.template import Template

    t = Template("py3o_example_template.odt", "py3o_example_output.odt")

    t.set_image_path('logo', 'images/new_logo.png')


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

    for i in xrange(1000):
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
    t.render(data)

Contributors
============

  - `Houzéfa Abbasbay`_
  - Torsten Irländer
  - `sir_sigurd`_

.. _Houzéfa Abbasbay:https://bitbucket.org/houzefa-abba
.. _sir_sigurd:https://bitbucket.org/sir_sigurd
