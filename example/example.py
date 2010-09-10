from py3o.template import Template

t = Template("py3o_example_template.odt", "py3o_example_output.odt")

class Item(object): pass

items = list()

item1 = Item()
item1.val1 = 'Item1 Value1'
item1.val2 = 'Item1 Value2'
item1.val3 = 'Item1 Value3'
item1.Currency = 'EUR'
item1.Amount = '12345.35'
item1.InvoiceRef = 'Reference #1234'

item2 = Item()
item2.val1 = 'Item2 Value1'
item2.val2 = 'Item2 Value2'
item2.val3 = 'Item2 Value3'
item2.Currency = 'EUR'
item2.Amount = '6666.77'
item2.InvoiceRef = 'Reference #7777'

items.append(item1)
items.append(item2)

document = Item()
document.total = '9999999999999.999'

data = dict(items=items, document=document)
t.render(data)


