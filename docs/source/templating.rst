Template system in LibreOffice
==============================

Define variables
~~~~~~~~~~~~~~~~

If you have read the Python code above you have seen that we pushed
a dictionnary to our template.render() method. We must now declare the attributes you want to use from those variables in LibreOffice.

This is done by creating user fields with specific names. The naming scheme is
important because it permits differentiate real user fields, which have their own purpose we won't discuss in this document, from the ones we define in order to easily use them in our templates.

User fields should be defined as follows:

  .. image:: images/fields_definition.png

the "py3o." prefix is mandatory. Without this prefix the templating system will not be able to find your variables.

The important part is the variable name. This is what is used by py3o.template to find your variables. The value (in our screenshot: Invoice.Reference) is only some sugar that helps read the template in OpenOffice.

You should take care to pick a nice and meaningfull value so that your end-users know what they will get just by looking at the document without being forced to open the variable definition.

Use control structures
~~~~~~~~~~~~~~~~~~~~~~

Every control structure must be added to you document using a specially formatted hyperlink::

    link = py3o://for="item in items"
    text = for="item in items"

At the moment you can use "for" and "if".

In our example document we want to use a "for" loop to iterate over all the items
that were given to our template by the render() method.

Here is an example setup:

  .. image:: images/for_loop_definition.png

It is especially important to have the link value equivalent to the text value as in the example above.

Once you save your hyperlink, your py3o:// URL will become URL escaped which is fine.

Every control structure must be closed by a corresponding closing tag. In our case we must insert a "/for" hyperlink::

    link = py3o:///for
    text = /for

Defined in the user interface as such:

  .. image:: images/for_loop_close_definition.png

Insert variables
~~~~~~~~~~~~~~~~

Once you have setup variables and defined some optional control structures you can start inserting variable inside the document.

The best way it to use the menu::

    Insert > Field > Other

then choose User fields in the field type selection, then choose your desired variable in the second column and then finally click the green arrow at the bottom:

  .. image:: images/fields_all_usage.png

This operation will insert your user field near your cursor. This field will be replace at template.render() time by the real value coming from the dataset (see aboove python code)

Example document
~~~~~~~~~~~~~~~~

You can find an example template in `our source tree`_

.. _our source tree: https://bitbucket.org/faide/py3o.template/src/889d8bc11290d3300f5da12f44ac98b7a6af9399/example/py3o_example_template.odt?at=default

Here is a screenshot to show you some control structures (for and if) in action. As you can see you can use these control structures even inside tables:

  .. image:: images/full_document_exemple.png


