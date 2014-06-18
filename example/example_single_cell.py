from py3o.template import Template

t = Template("py3o_example_template_single_cell.odt", "py3o_example_output_single_cell.odt")

t.set_image_path('logo', 'images/new_logo.png')


class Item(object):
    pass

items = list()

item1 = Item()
item1.val1 = 'Item1 Value1'
item1.val2 = 'Item1 Value2'
item1.val3 = 'Item1 Value3'
item1.Currency = 'EUR'
item1.Amount = '12,345.35'
item1.InvoiceRef = '#1234'
items.append(item1)

for i in xrange(1000):
    item = Item()
    item.val1 = 'Item%s Value1' % i
    item.val2 = 'Item%s Value2' % i
    item.val3 = 'Item%s Value3' % i
    item.Currency = 'EUR'
    item.Amount = '6,666.77'
    item.InvoiceRef = 'Reference #%04d' % i
    items.append(item)

document = Item()
document.total = '9,999,999,999,999.999'

data = dict(items=items, document=document)
t.render(data)

