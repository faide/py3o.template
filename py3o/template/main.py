# -*- encoding: utf-8 -*-
import decimal
import os

import lxml.etree
import zipfile

from copy import copy
from io import BytesIO
from uuid import uuid4

try:
    # python 2.x
    from urllib import unquote
except ImportError:
    # python 3.x
    from urllib.parse import unquote

from genshi.template import MarkupTemplate
from genshi.filters.transform import Transformer

from pyjon.utils import get_secure_filename

GENSHI_URI = 'http://genshi.edgewall.org/'
PY3O_URI = 'http://py3o.org/'

# Images are stored in the "Pictures" directory and prefixed with "py3o-".
# Saving images in a sub-directory would be cleaner but doesn't seem to be
# supported...
PY3O_IMAGE_PREFIX = 'Pictures/py3o-'


class TemplateException(ValueError):
    """some client code is used to catching ValueErrors, let's keep the old
    codebase hapy
    """
    pass


def move_siblings(start, end, new_):
    """a helper function that will replace a start/end node pair
    by a new containing element, effectively moving all in-between siblings
    This is particularly helpful to replace for /for loops in tables
    with the content resulting from the iteration

    This function call returns None. The parent xml tree is modified in place

    @param start: the starting xml node
    @type start: lxml.etree.Element

    @param end: the ending xml node
    @type end: lxml.etree.Element

    @param new_: the new xml element that will replace the start/end pair
    @type new_: lxlm.etree.Element

    @returns: None
    """
    old_ = start.getparent()
    new_.append(copy(start))

    # get all siblings
    for node in start.itersiblings():
        new_.append(node)
        if node is end:
            # if this is already the end boundary, then we are done
            break

    # replace start boundary with new node
    old_.replace(start, new_)


def get_list_transformer(namespaces):
    """this function returns a transformer to
     find all list elements and recompute their xml:id.
    Because if we duplicate lists we create invalid XML.
    Each list must have its own xml:id

    This is important if you want to be able to reopen the produced
     document wih an XML parser. LibreOffice will fix those ids itself
     silently, but lxml.etree.parse will bork on such duplicated lists
    """
    return Transformer(
        '//list[namespace-uri()="%s"]' % namespaces.get(
            'text'
        )
    ).attr(
        '{%s}id' % 'http://www.w3.org/XML/1998/namespace',
        lambda *args: "list{}".format(uuid4().hex)
    )


def get_instructions(content_tree, namespaces):
    # find all links that have a py3o
    xpath_expr = "//text:a[starts-with(@xlink:href, 'py3o://')]"
    return content_tree.xpath(
        xpath_expr,
        namespaces=namespaces
    )


def get_user_fields(content_tree, namespaces):
    field_expr = "//text:user-field-decl[starts-with(@text:name, 'py3o.')]"
    return content_tree.xpath(
        field_expr,
        namespaces=namespaces
    )


class Template(object):
    templated_files = ['content.xml', 'styles.xml', 'META-INF/manifest.xml']

    def __init__(self, template, outfile):
        """A template object exposes the API to render it to an OpenOffice
        document.

        @param template: a py3o template file. ie: a OpenDocument with the
        proper py3o markups
        @type template: a string representing the full path name to a py3o
        template file.

        @param outfile: the desired file name for the resulting ODT document
        @type outfile: a string representing the full filename for output
        """
        self.template = template
        self.outputfilename = outfile
        self.infile = zipfile.ZipFile(self.template, 'r')

        self.content_trees = [
            lxml.etree.parse(BytesIO(self.infile.read(filename)))
            for filename in self.templated_files
        ]
        self.tree_roots = [tree.getroot() for tree in self.content_trees]

        self.__prepare_namespaces()

        self.images = {}
        self.output_streams = []

    def __prepare_namespaces(self):
        """create proper namespaces for our document
        """
        # create needed namespaces
        self.namespaces = dict(
            text="urn:text",
            draw="urn:draw",
            table="urn:table",
            office="urn:office",
            xlink="urn:xlink",
            svg="urn:svg",
            manifest="urn:manifest",
        )

        # copy namespaces from original docs
        for tree_root in self.tree_roots:
            self.namespaces.update(tree_root.nsmap)

        # remove any "root" namespace as lxml.xpath do not support them
        self.namespaces.pop(None, None)

        # declare the genshi namespace
        self.namespaces['py'] = GENSHI_URI
        # declare our own namespace
        self.namespaces['py3o'] = PY3O_URI

    def get_user_instructions(self):
        """ Public method to help report engine to find all instructions
        """
        res = []
        for e in get_instructions(self.content_trees[0], self.namespaces):
            childs = e.getchildren()
            if childs:
                res.append(childs.text)
            else:
                res.append(e.text)
        return res

    def __handle_instructions(self):

        opened_starts = list()
        starting_tags = list()
        closing_tags = dict()

        for content_tree in self.content_trees:
            for link in get_instructions(content_tree, self.namespaces):
                py3o_statement = unquote(
                    link.attrib['{%s}href' % self.namespaces['xlink']]
                )
                # remove the py3o://
                py3o_base = py3o_statement[7:]

                if not py3o_base.startswith("/"):
                    opened_starts.append(link)
                    starting_tags.append((content_tree, link, py3o_base))

                else:
                    if not opened_starts:
                        raise TemplateException(
                            "No open instruction for %s" % py3o_base)

                    closing_tags[id(opened_starts.pop())] = (
                        content_tree, link
                    )

        return starting_tags, closing_tags

    def __handle_link(self, content_tree, link, py3o_base, closing_link):
        """transform a py3o link into a proper Genshi statement
        rebase a py3o link at a proper place in the tree
        to be ready for Genshi replacement
        """
        # OLD open office version
        if not link.text is None:
            if not link.text == py3o_base:
                msg = "url and text do not match in '%s'" % link.text
                raise TemplateException(msg)

        # new open office version
        else:
            if not link[0].text == py3o_base:
                msg = "url and text do not match in '%s'" % link.text
                raise TemplateException(msg)

        # find out if the instruction is inside a table
        parent = link.getparent()
        if parent.getparent() is not None and parent.getparent().tag == (
            "{%s}table-cell" % self.namespaces['table']
        ):
            # we are in a table
            opening_paragraph = parent
            opening_cell = opening_paragraph.getparent()

            # same for closing
            closing_paragraph = closing_link.getparent()
            closing_cell = closing_paragraph.getparent()

            if opening_cell == closing_cell:
                # block is fully in a single cell
                opening_row = opening_paragraph
                closing_row = closing_paragraph
            else:
                opening_row = opening_cell.getparent()
                closing_row = closing_cell.getparent()

        elif parent.tag == "{%s}p" % self.namespaces['text']:
            # we are in a text paragraph
            opening_row = parent
            closing_row = closing_link.getparent()

        else:
            raise NotImplementedError(
                "We handle urls in tables or text paragraph only"
            )

        # max split is one
        instruction, instruction_value = py3o_base.split("=", 1)
        instruction_value = instruction_value.strip('"')

        attribs = dict()
        attribs['{%s}strip' % GENSHI_URI] = 'True'
        attribs['{%s}%s' % (GENSHI_URI, instruction)] = instruction_value

        genshi_node = lxml.etree.Element(
            'span',
            attrib=attribs,
            nsmap={'py': GENSHI_URI},
        )

        # remove links from tags
        opening_row.remove(link)
        closing_row.remove(closing_link)

        move_siblings(opening_row, closing_row, genshi_node)

    def get_user_variables(self):
        """a public method to help report engines to introspect
        a template and find what data it needs and how it will be
        used
        returns a list of user variable names"""
        # TODO: Check if some user fields are stored in other content_trees
        return [
            e.get('{%s}name' % e.nsmap.get('text'))
            for e in get_user_fields(self.content_trees[0], self.namespaces)
        ]

    def __prepare_userfield_decl(self):
        self.field_info = dict()

        for content_tree in self.content_trees:
            for userfield in get_user_fields(content_tree, self.namespaces):
                value = userfield.attrib[
                    '{%s}name' % self.namespaces['text']
                ][5:]
                value_type = userfield.attrib.get(
                    '{%s}value-type' % self.namespaces['office'],
                    'string'
                )

                self.field_info[value] = dict(name=value,
                                              value_type=value_type)

    def __prepare_usertexts(self):
        """Replace user-type text fields that start with "py3o." with genshi
        instructions.
        """

        field_expr = "//text:user-field-get[starts-with(@text:name, 'py3o.')]"

        for content_tree in self.content_trees:

            for userfield in content_tree.xpath(
                field_expr,
                namespaces=self.namespaces
            ):
                parent = userfield.getparent()
                value = userfield.attrib[
                    '{%s}name' % self.namespaces['text']
                ][5:]
                # value_type = userfield.attrib.get(
                #     '{%s}value-type' % self.namespaces['office'],
                #     'string'
                # )
                value_type = self.field_info[value]['value_type']

                # we try to override global var type with local settings
                value_type_attr = '{%s}value-type' % self.namespaces['office']
                rec = 0
                npar = parent

                # special case for float which has a value info on top level
                # overriding local value
                found_node = False
                while rec <= 5:
                    if npar is None:
                        break

                    if value_type_attr in npar.attrib:
                        value_type = npar.attrib[value_type_attr]
                        found_node = True
                        break

                    npar = npar.getparent()

                if value_type == 'float':
                    value_attr = '{%s}value' % self.namespaces['office']
                    rec = 0

                    if found_node:
                        npar.attrib[value_attr] = "${%s}" % value
                    else:
                        npar = userfield
                        while rec <= 7:
                            if npar is None:
                                break

                            if value_attr in npar.attrib:
                                npar.attrib[value_attr] = "${%s}" % value
                                break

                            npar = npar.getparent()

                    value = "format_float(%s)" % value

                if value_type == 'percentage':
                    del npar.attrib[value_attr]
                    value = "format_percentage(%s)" % value
                    npar.attrib[value_type_attr] = "string"

                attribs = dict()
                attribs['{%s}strip' % GENSHI_URI] = 'True'
                attribs['{%s}content' % GENSHI_URI] = value

                genshi_node = lxml.etree.Element(
                    'span',
                    attrib=attribs,
                    nsmap={'py': GENSHI_URI}
                )

                if userfield.tail:
                    genshi_node.tail = userfield.tail

                parent.replace(userfield, genshi_node)

    def __replace_image_links(self):
        """Replace links of placeholder images (the name of which starts with
        "py3o.") to point to a file saved the "Pictures" directory of the
        archive.
        """

        image_expr = "//draw:frame[starts-with(@draw:name, 'py3o.')]"

        for content_tree in self.content_trees:

            # Find draw:frame tags.
            for draw_frame in content_tree.xpath(
                image_expr,
                namespaces=self.namespaces
            ):
                # Find the identifier of the image (py3o.[identifier]).
                image_id = draw_frame.attrib[
                    '{%s}name' % self.namespaces['draw']
                ][5:]
                if image_id not in self.images:
                    raise TemplateException(
                        "Can't find data for the image named 'py3o.%s'; make "
                        "sure it has been added with the set_image_path or "
                        "set_image_data methods."
                        % image_id
                    )

                # Replace the xlink:href attribute of the image to point to
                # ours.
                image = draw_frame[0]
                image.attrib[
                    '{%s}href' % self.namespaces['xlink']
                ] = PY3O_IMAGE_PREFIX + image_id

    def __add_images_to_manifest(self):
        """Add entries for py3o images into the manifest file."""

        xpath_expr = "//manifest:manifest[1]"

        for content_tree in self.content_trees:

            # Find manifest:manifest tags.
            manifest_e = content_tree.xpath(
                xpath_expr,
                namespaces=self.namespaces
            )
            if not manifest_e:
                continue

            for identifier in self.images.keys():
                # Add a manifest:file-entry tag.
                lxml.etree.SubElement(
                    manifest_e[0],
                    '{%s}file-entry' % self.namespaces['manifest'],
                    attrib={
                        '{%s}full-path' % self.namespaces['manifest']: (
                            PY3O_IMAGE_PREFIX + identifier
                        ),
                        '{%s}media-type' % self.namespaces['manifest']: '',
                    }
                )

    def render_tree(self, data):
        """prepare the flows without saving to file
        this method has been decoupled from render_flow to allow better
        unit testing
        """
        new_data = dict(
            decimal=decimal,
            format_float=(
                lambda val: (
                    isinstance(
                        val, decimal.Decimal
                    ) or isinstance(
                        val, float
                    )
                ) and str(val).replace('.', ',') or val
            ),
            format_percentage=(
                lambda val: ("%0.2f %%" % val).replace('.', ',')
            )
        )

        # first we need to transform the py3o template into a valid
        # Genshi template.
        starting_tags, closing_tags = self.__handle_instructions()
        for content_tree, link, py3o_base in starting_tags:
            self.__handle_link(
                content_tree,
                link,
                py3o_base,
                closing_tags[id(link)][1]
            )

        self.__prepare_userfield_decl()
        self.__prepare_usertexts()

        self.__replace_image_links()
        self.__add_images_to_manifest()

        for fnum, content_tree in enumerate(self.content_trees):
            template = MarkupTemplate(
                lxml.etree.tostring(content_tree.getroot())
            )
            # then we need to render the genshi template itself by
            # providing the data to genshi

            template_dict = {}
            template_dict.update(data.items())
            template_dict.update(new_data.items())

            self.output_streams.append(
                (
                    self.templated_files[fnum],
                    template.generate(**template_dict)
                )
            )

    def render_flow(self, data):
        """render the OpenDocument with the user data

        @param data: the input stream of user data. This should be a dictionary
        mapping, keys being the values accessible to your report.
        @type data: dictionary
        """

        self.render_tree(data)

        # then reconstruct a new ODT document with the generated content
        for status in self.__save_output():
            yield status

    def render(self, data):
        """render the OpenDocument with the user data

        @param data: the input stream of userdata. This should be a dictionary
        mapping, keys being the values accessible to your report.
        @type data: dictionary
        """
        for status in self.render_flow(data):
            if not status:
                raise TemplateException("unknown template error")

    def set_image_path(self, identifier, path):
        """Set data for an image mentioned in the template.

        @param identifier: Identifier of the image; refer to the image in the
        template by setting "py3o.[identifier]" as the name of that image.
        @type identifier: string

        @param path: Image path on the file system
        @type path: string
        """

        f = open(path, 'rb')
        self.set_image_data(identifier, f.read())
        f.close()

    def set_image_data(self, identifier, data):
        """Set data for an image mentioned in the template.

        @param identifier: Identifier of the image; refer to the image in the
        template by setting "py3o.[identifier]" as the name of that image.
        @type identifier: string

        @param data: Contents of the image.
        @type data: binary
        """

        self.images[identifier] = data

    def __save_output(self):
        """Saves the output into a native OOo document format.
        """
        out = zipfile.ZipFile(self.outputfilename, 'w')

        for info_zip in self.infile.infolist():

            if info_zip.filename in self.templated_files:
                # Template file - we have edited these.

                # get a temp file
                streamout = open(get_secure_filename(), "w+b")
                fname, output_stream = self.output_streams[
                    self.templated_files.index(info_zip.filename)
                ]

                transformer = get_list_transformer(self.namespaces)
                remapped_stream = output_stream | transformer

                # write the whole stream to it
                for chunk in remapped_stream.serialize():
                    streamout.write(chunk.encode('utf-8'))
                    yield True

                # close the temp file to flush all data and make sure we get
                # it back when writing to the zip archive.
                streamout.close()

                # write the full file to archive
                out.write(streamout.name, fname)

                # remove temp file
                os.unlink(streamout.name)

            else:
                # Copy other files straight from the source archive.
                out.writestr(info_zip, self.infile.read(info_zip.filename))

        # Save images in the "Pictures" sub-directory of the archive.
        for identifier, data in self.images.items():
            out.writestr(PY3O_IMAGE_PREFIX + identifier, data)

        # close the zipfile before leaving
        out.close()
        yield True
