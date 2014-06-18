Templating with LibreOffice
==============================

If you have read the Python code above you have seen that we pushed
a dictionary to our template.render() method.

We must now declare the attributes you want to use from those variables in LibreOffice.

Use control structures
~~~~~~~~~~~~~~~~~~~~~~

At the moment "for" and "if" controls are available.

In our example python code we have a dataset that contains a list of items. This list itself is named "items" and we want to iterate on all the items.

We should add a for loop using an hyperlink.

Every control structure must be added to you document using a specially formatted hyperlink::

    link = py3o://for="item in items"
    text = for="item in items"

Here is an example setup:

  .. image:: images/for_loop_definition.png

It is especially important to have the link value equivalent to the text value as in the example above.

Once you save your hyperlink, your py3o:// URL will become URL escaped which is fine.

Every control structure must be closed by a corresponding closing tag. In our case we must insert a "/for" hyperlink::

    link = py3o:///for
    text = /for

Defined in the user interface as such:

  .. image:: images/for_loop_close_definition.png

Define variables
~~~~~~~~~~~~~~~~

This is done by creating user fields (CTRL-F2) with specific names. The naming scheme is
important because it permits differentiate real user fields, which have their own purpose we won't discuss in this document, from the ones we define in our templates.

Since we are inside a for loop that defines a variable names "items" we want to create a user variable in LibreOffice that is named like this::

    py3o.item.Amount

The "Amount" is not something we invent. This is because the item variable is an object coming from your python code. And we defined the Amount attribute back then.

In LibreOffice, user fields can be defined by pressing CTRL-F2 then choosing variables and user-fields:

  .. image:: images/fields_definition.png

You must enter a value in name and value then press the green arrow to the right.

the "py3o." prefix is mandatory. Without this prefix the templating system will not be able to find your variables.

The value (in our screenshot: Invoice.Reference) is only some sugar that helps read the template in OpenOffice.

You should take care to pick a nice and meaningfull value so that your end-users know what they will get just by looking at the document without being forced to open the variable definition.

Data Dictionnary
~~~~~~~~~~~~~~~~

If you are a developper and want to provide some kind of raw document for your users, it is a good idea to create all the relevent user variables yourself. This is what we call in our jargon creating the data dictionary.

This is especially important because the variable names (eg: py3o.variable.attribute) are linked to your code. And remember that your users do not have access to the code.

You should put them in a position where they can easily pick from a list instead of being forced to ask you what are the available variables.

Insert variables
~~~~~~~~~~~~~~~~

Once you have setup variables and defined some optional control structures you can start inserting variables inside the document.

The best way it to use the menu::

    Insert > Field > Other

or just press::

    CTRL-F2

then choose User fields in the field type selection, then choose your desired variable in the second column and then finally click insert at the bottom:

  .. image:: images/fields_all_usage.png

This operation will insert your user field near your cursor. This field will be replaced at template.render() time by the real value coming from the dataset (see above python code)

Insert placeholder images
-------------------------

py3o.template can replace images on-the-fly. To add an image field, add a regular image as a placeholder, open its properties and prefix its name with "py3o."; the rest of the image name is then its identifier:

  .. image:: images/image_name.png

The Python code has to call set_image_path or set_image_data to let py3o know about the image; check our example code.

Example document
~~~~~~~~~~~~~~~~

You can find an example template in `our source tree`_

.. _our source tree: https://bitbucket.org/faide/py3o.template/src/889d8bc11290d3300f5da12f44ac98b7a6af9399/example/py3o_example_template.odt?at=default

Here is a screenshot to show you some control structures (for and if) in action. As you can see you can use these control structures even inside tables:

  .. image:: images/full_document_exemple.png


