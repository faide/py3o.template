from py3o.template import Template

t = Template(
    "py3o_example_template_page_break.odt",
    "py3o_example_page_break_output.odt"
)


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

for i in xrange(10):
    item = Item()
    item.val1 = 'Item%s Value1' % i
    item.val2 = 'Item%s Value2' % i
    item.val3 = 'Item%s Value3' % i
    item.Currency = 'EUR'
    item.Amount = '6666.77'
    item.InvoiceRef = 'Reference #%04d' % i
    items.append(item)

item1 = Item()
item1.val1 = 'Item1 Value1'
item1.val2 = 'Item1 Value2'
item1.val3 = 'Item1 Value3'
item1.Currency = 'EUR'
item1.Amount = '12345.35'
item1.InvoiceRef = '#1234'
items.append(item1)

document = Item()
document.total = 999.99

data = dict(items=items, document=document)
t.render(data)
