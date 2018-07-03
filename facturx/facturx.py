import io
import os
import yaml
import codecs
from io import BytesIO
from lxml import etree
from tempfile import NamedTemporaryFile
from datetime import datetime
import os.path
import mimetypes
import hashlib
from PyPDF2 import PdfFileReader
from PyPDF2.generic import IndirectObject
import json

from .flavors import xml_flavor
from .logger import logger
from .pdfwriter import FacturXPDFWriter

# Python 2 and 3 compat
try:
    file_types = (file, io.IOBase)
except NameError:
    file_types = (io.IOBase,)
unicode = str

__all__ = ['FacturX']


class FacturX(object):
    """Represents an electronic PDF invoice with embedded XML metadata following the
    Factur-X standard.

    The source of truth is always the underlying XML tree. No copy of field
    data is kept. Manipulation of the XML tree is either done via Python-style
    dict access (available for the most common fields) or by directly accessing
    the XML data on `FacturX.xml`.

    Attributes:
    - xml: xml tree of machine-readable representation.
    - pdf: underlying graphical PDF representation.
    - flavor: which flavor (Factur-x or Zugferd) to use.
    """

    def __init__(self, pdf_invoice, flavor='factur-x', level='minimum'):
        # Read PDF from path, pointer or string
        if isinstance(pdf_invoice, str) and pdf_invoice.endswith('.pdf') and os.path.isfile(pdf_invoice):
            with open(pdf_invoice, 'rb') as f:
                pdf_file = BytesIO(f.read())
        elif isinstance(pdf_invoice, str):
            pdf_file = BytesIO(pdf_invoice)
        elif isinstance(pdf_invoice, file_types):
            pdf_file = pdf_invoice
        else:
            raise TypeError(
                "The first argument of the method get_facturx_xml_from_pdf must "
                "be either a string or a file (it is a %s)." % type(pdf_invoice))

        xml = self._xml_from_file(pdf_file)
        self.pdf = pdf_file

        # PDF has metadata embedded
        if xml is not None:
            self.xml = xml
            self.flavor = xml_flavor.XMLFlavor(xml)
            logger.info('Read existing XML from PDF. Flavor: %s', self.flavor.name)
        # No metadata embedded. Create from template.
        else:
            self.flavor, self.xml = xml_flavor.XMLFlavor.from_template(flavor, level)
            logger.info('PDF does not have XML embedded. Adding from template.')

        self.flavor.check_xsd(self.xml)
        self._namespaces = self.xml.nsmap

    def read_xml(self):
        """Use XML data from external file. Replaces existing XML or template."""
        pass

    def _xml_from_file(self, pdf_file):
        pdf = PdfFileReader(pdf_file)
        pdf_root = pdf.trailer['/Root']
        if '/Names' not in pdf_root or '/EmbeddedFiles' not in pdf_root['/Names']:
            logger.info('No existing XML file found.')
            return None

        for file in pdf_root['/Names']['/EmbeddedFiles']['/Names']:
            if isinstance(file, IndirectObject):
                obj = file.getObject()
                if obj['/F'] in xml_flavor.valid_xmp_filenames():
                    xml_root = etree.fromstring(obj['/EF']['/F'].getData())
                    xml_content = xml_root
                    xml_filename = obj['/F']
                    logger.info(
                        'A valid XML file %s has been found in the PDF file',
                        xml_filename)
                    return xml_content

    def __getitem__(self, field_name):
        path = self.flavor._get_xml_path(field_name)
        value = self.xml.xpath(path, namespaces=self._namespaces)
        if value is not None:
            value = value[0].text
        if 'date' in field_name:
            value = datetime.strptime(value, '%Y%m%d')
        return value

    def __setitem__(self, field_name, value):
        path = self.flavor._get_xml_path(field_name)
        res = self.xml.xpath(path, namespaces=self._namespaces)
        if len(res) > 1:
            raise LookupError('Multiple nodes found for this path. Refusing to edit.')

        if 'date' in field_name:
            assert isinstance(value, datetime), 'Please pass date values as DateTime() object.'
            value = value.strftime('%Y%m%d')
            res[0].attrib['format'] = '102'
            res[0].text = value
        else:
            res[0].text = value

    def is_valid(self):
        """Make every effort to validate the current XML.

        Checks:
        - all required fields are present and have values.
        - XML is valid
        - ...

        Returns: true/false (validation passed/failed)
        """
        # validate against XSD
        try:
            self.flavor.check_xsd(self.xml)
        except Exception:
            return False

        # Check for required fields
        fields_data = xml_flavor.FIELDS
        for field in fields_data.keys():
            if fields_data[field]['_required']:
                r = self.xml.xpath(fields_data[field]['_path'][self.flavor.name], namespaces=self._namespaces)
                if not len(r):
                    logger.error("Required field '%s' is not present", field)
                    return False
                elif r[0].text is None:
                    logger.error("Required field %s doesn't contain any value", field)
                    return False

        return True
    
    def write_pdf(self, path):
        pdfwriter = FacturXPDFWriter(self)
        with open(path, 'wb') as output_f:
            pdfwriter.write(output_f)

        logger.info('XML file added to PDF invoice')
        return True

    @property
    def xml_str(self):
        """Calculate MD5 checksum of XML file. Used for PDF attachment."""
        return etree.tostring(self.xml, pretty_print=True)

    def write_xml(self, path):
        with open(path, 'wb') as f:
            f.write(self.xml_str)

    def __make_dict(self):
        fields_data = xml_flavor.FIELDS
        flavor = self.flavor.name

        output_dict = {}
        for field in fields_data.keys():
            try:
                r = self.xml.xpath(fields_data[field]['_path'][flavor], namespaces=self._namespaces)
                output_dict[field] = r[0].text
            except IndexError:
                output_dict[field] = None

        return output_dict

    def write_json(self, json_file_path='output.json'):
        json_output = self.__make_dict()
        # if self.is_valid():
        #     with open(json_file_path, 'w') as json_file:
        #         logger.info("Exporting JSON to %s", json_file_path)
        #         json.dump(json_output, json_file, indent=4, sort_keys=True)

        with open(json_file_path, 'w') as json_file:
                logger.info("Exporting JSON to %s", json_file_path)
                json.dump(json_output, json_file, indent=4, sort_keys=True)

    def write_yml(self, yml_file_path='output.yml'):
        yml_output = self.__make_dict()
        # if self.is_valid():
        #     with open(yml_file_path, 'w') as yml_file:
        #         logger.info("Exporting YAML to %s", yml_file_path)
        #         yaml.dump(yml_output, yml_file, default_flow_style=False)

        with open(yml_file_path, 'w') as yml_file:
                logger.info("Exporting YAML to %s", yml_file_path)
                yaml.dump(yml_output, yml_file, default_flow_style=False)
