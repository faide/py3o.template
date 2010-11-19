import lxml.etree
import zipfile
from StringIO import StringIO
import urllib
from genshi.template import MarkupTemplate
from pyjon.utils import get_secure_filename
import os

GENSHI_URI = 'http://genshi.edgewall.org/'
PY3O_URI = 'http://py3o.org/'

def move_siblings(start, end, new_):
    old_ = start.getparent()

    # copy any tail we find
    if start.tail:
        new_.text = start.tail

    # get all siblings
    for node in start.itersiblings():
        if not node is end:
            # and stuff them in our new node
            new_.append(node)
        else:
            # if this is already the end boundary, then we are done
            break

    # replace start boundary with new node
    old_.replace(start, new_)
    # remove ending boundary
    old_.remove(end)

class Template(object):

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

        self.py3ocontent = lxml.etree.parse(StringIO(self.infile.read("content.xml")))
        self.py3oroot = self.py3ocontent.getroot()
        self.__prepare_namespaces()

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
            )

        # copy namespaces from original doc
        self.namespaces.update(self.py3oroot.nsmap)

        # remove any "root" namespace as lxml.xpath do not support them
        self.namespaces.pop(None, None)

        # declare the genshi namespace
        self.namespaces['py'] = GENSHI_URI
        # declare our own namespace
        self.namespaces['py3o'] = PY3O_URI

    def __handle_instructions(self):
        # find all links that have a py3o
        xpath_expr = "//text:a[starts-with(@xlink:href, 'py3o://')]"

        opened_starts = list()
        starting_tags = list()
        closing_tags = dict()

        for link in self.py3ocontent.xpath(xpath_expr, namespaces=self.namespaces):
            py3o_statement = urllib.unquote(link.attrib['{%s}href' % self.namespaces['xlink']])
            # remove the py3o://
            py3o_base = py3o_statement[7:]

            if not py3o_base.startswith("/"):
                opened_starts.append(link)
                starting_tags.append((link, py3o_base))

            else:
                closing_tags[id(opened_starts.pop())] = link

        return starting_tags, closing_tags

    def __handle_link(self, link, py3o_base, closing_link):
        """transform a py3o link into a proper Genshi statement
        rebase a py3o link a a proper place in the tree
        to be ready for Genshi replacement
        """
        if not link.text == py3o_base:
            msg = "url and text do not match in '%s'" % link.text
            raise ValueError(msg)

        if link.getparent().getparent().tag == "{%s}table-cell" % self.namespaces['table']:
            # we are in a table
            opening_paragraph = link.getparent()
            opening_cell = opening_paragraph.getparent()
            opening_row = opening_cell.getparent()

            # same for closing
            closing_paragraph = closing_link.getparent()
            closing_cell = closing_paragraph.getparent()
            closing_row = closing_cell.getparent()

        elif link.getparent().tag == "{%s}p" % self.namespaces['text']:
            # we are in a text paragraph
            opening_row = link.getparent()
            closing_row = closing_link.getparent()

        else:
            raise NotImplementedError("We handle urls in tables or text paragraph only")

        # max split is one
        instruction, instruction_value = py3o_base.split("=", 1)
        instruction_value = instruction_value.strip('"')

        attribs = dict()
        attribs['{%s}strip' % GENSHI_URI] = 'True'
        attribs['{%s}%s' % (GENSHI_URI, instruction)] = instruction_value

        genshi_node = lxml.etree.Element('span',
                attrib=attribs, nsmap={'py': GENSHI_URI})

        move_siblings(opening_row, closing_row, genshi_node)

    def __prepare_usertexts(self):
        """user-field-get"""
        xpath_expr = "//text:user-field-get[starts-with(@text:name, 'py3o.')]"

        for userfield in self.py3ocontent.xpath(xpath_expr, namespaces=self.namespaces):
            parent = userfield.getparent()
            value = userfield.attrib['{%s}name' % self.namespaces['text']][5:]

            attribs = dict()
            attribs['{%s}strip' % GENSHI_URI] = 'True'
            attribs['{%s}content' % GENSHI_URI] = value

            genshi_node = lxml.etree.Element('span',
                    attrib=attribs, nsmap={'py': GENSHI_URI})

            if userfield.tail:
                genshi_node.tail = userfield.tail

            parent.replace(userfield, genshi_node)

    def render_flow(self, data):
        """render the OpenDocument with the user data

        @param data: the input stream of userdata. This should be a
        dictionnary mapping, keys being the values accessible to your
        report.
        @type data: dictionnary
        """

        # first we need to transform the py3o template into a valid
        # Genshi template.
        starting_tags, closing_tags = self.__handle_instructions()
        for link, py3o_base in starting_tags:
            self.__handle_link(link, py3o_base, closing_tags[id(link)])

        self.__prepare_usertexts()

        #out = open("content.xml", "w+")
        #out.write(lxml.etree.tostring(self.py3ocontent.getroot()))
        #out.close()

        template = MarkupTemplate(lxml.etree.tostring(self.py3ocontent.getroot()))
        # then we need to render the genshi template itself by
        # providing the data to genshi
        
        self.outputstream = template.generate(**data)

        # then reconstruct a new ODT document with the generated content
        for status in self.__save_output():
            yield status

    def render(self, data):
        """render the OpenDocument with the user data

        @param data: the input stream of userdata. This should be a
        dictionnary mapping, keys being the values accessible to your
        report.
        @type data: dictionnary
        """
        for status in self.render_flow(data):
            if not status:
                raise ValueError, "unknown error"

    def __save_output(self):
        """Saves the output into a native OOo document format.
        """
        out = zipfile.ZipFile(self.outputfilename, 'w')

        # copy everything from the source archive expect content.xml
        for info_zip in self.infile.infolist():
            if not info_zip.filename == "content.xml":
                out.writestr(info_zip,
                        self.infile.read(info_zip.filename))

            else:
                # get a temp file
                streamout = open(get_secure_filename(), "w+b")

                # write the whole stream to it
                for chunk in self.outputstream.serialize():
                    streamout.write(chunk.encode('utf-8'))
                    yield True

                # close the temp file to flush all data and make sure we get
                # it back when writing to the zip archive.
                streamout.close()

                # write the full file to archive
                out.write(streamout.name, "content.xml")

                # remove tempfile
                os.unlink(streamout.name)

        # close the zipfile before leaving
        out.close()
        yield True
