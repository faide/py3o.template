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
the py3o.renderserver on it.

Example Usage
=============

Below is an example that you can find in the source tarball inside the examples
directory.

::

    from py3o.template import Template

    t = Template("py3o_example_template.odt", "py3o_example_output.odt")

    t.set_image_path('logo', 'dummy_logo.png')


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

Template design
===============

Inserting variables
-------------------

In order to insert py3o variables inside the LibreOffice template file, use
the dialog box accessible from Insert > Fields > Variables.

In "Type", select" "User Field".
In "Format", select "Text".

Type the variable to use in the "Name" field, prefixed with "py3o."; for
example:
    py3o.document.total

In "Value", type any string of your choice; that string will be displayed in
the template and replaced at parsing time by the contents of the variable.

Structure keywords
------------------

Some keywords are available to control the content:
    - "if" inserts an optional block.
    - "for" allows looping through a container.

Keywords are inserted as hyperlinks, with the syntax:
    keyword="expression"

Keyword blocks have to be terminated with another hyperlink; syntax:
    /keyword

Page breaks
-----------

To insert page breaks, just use regular LibreOffice page breaking features.

Images
------

py3o.template can replace images on-the-fly. To add an image field, add a
regular image as a placeholder, open its properties and prefix its name with
"py3o."; the rest of the image name is then its identifier.

Call one of the following methods to set image data:
    - set_image_path
    - set_image_data
