# -*- coding: utf-8 -*-
# Copyright 2016-2018, Alexis de Lattre <alexis.delattre@akretion.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * The name of the authors may not be used to endorse or promote products
#      derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDERS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# TODO list:
# - have both python2 and python3 support
# - add automated tests (currently, we only have tests at odoo module level)
# - keep original metadata by copy of pdf_tailer[/Info] ?

from ._version import __version__
import io
import os
import yaml
import codecs
from io import BytesIO
from lxml import etree
from tempfile import NamedTemporaryFile
from datetime import datetime
from PyPDF2 import PdfFileWriter, PdfFileReader
from PyPDF2.generic import DictionaryObject, DecodedStreamObject,\
    NameObject, createStringObject, ArrayObject, IndirectObject
from pkg_resources import resource_filename
import os.path
import mimetypes
import hashlib

from .logger import logger

# Python 2 and 3 compat
try:
    file_types = (file, io.IOBase)
except NameError:
    file_types = (io.IOBase,)
unicode = str

class FacturXPDFWriter(PdfFileWriter):
    def __init__(self, facturx, pdf_metadata=None):
        """Take a FacturX instance and write the XML to the attached PDF file"""

        super(FacturXPDFWriter, self).__init__()
        # TODO: Can handle str/paths and ByteIO?
        self.factx = facturx

        original_pdf = PdfFileReader(facturx.pdf)
        # Extract /OutputIntents obj from original invoice
        output_intents = _get_original_output_intents(original_pdf)
        self.appendPagesFromReader(original_pdf)

        original_pdf_id = original_pdf.trailer.get('/ID')
        logger.debug('original_pdf_id=%s', original_pdf_id)
        if original_pdf_id:
            self._ID = original_pdf_id
            # else : generate some ?

        if pdf_metadata is None:
            base_info = {
                'seller': self.factx['seller'],
                'number': self.factx['invoice_number'],
                'date': self.factx['date'],
                'doc_type': self.factx['type'],
                }
            pdf_metadata = _base_info2pdf_metadata(base_info)
        else:
            # clean-up pdf_metadata dict
            for key, value in pdf_metadata.iteritems():
                if not isinstance(value, (str, unicode)):
                    pdf_metadata[key] = ''

        self._update_metadata_add_attachment(pdf_metadata, output_intents)


    def _update_metadata_add_attachment(self, pdf_metadata, output_intents):
        '''This method is inspired from the code of the addAttachment()
        method of the PyPDF2 lib'''
        
        # The entry for the file
        facturx_xml_str = self.factx.xml_str
        md5sum = hashlib.md5().hexdigest()
        md5sum_obj = createStringObject(md5sum)
        params_dict = DictionaryObject({
            NameObject('/CheckSum'): md5sum_obj,
            NameObject('/ModDate'): createStringObject(_get_pdf_timestamp()),
            NameObject('/Size'): NameObject(str(len(facturx_xml_str))),
            })
        file_entry = DecodedStreamObject()
        file_entry.setData(facturx_xml_str)  # here we integrate the file itself
        file_entry.update({
            NameObject("/Type"): NameObject("/EmbeddedFile"),
            NameObject("/Params"): params_dict,
            # 2F is '/' in hexadecimal
            NameObject("/Subtype"): NameObject("/text#2Fxml"),
            })
        file_entry_obj = self._addObject(file_entry)
        # The Filespec entry
        ef_dict = DictionaryObject({
            NameObject("/F"): file_entry_obj,
            NameObject('/UF'): file_entry_obj,
            })

        xmp_filename = self.factx.flavor.details['xmp_filename']
        fname_obj = createStringObject(xmp_filename)
        filespec_dict = DictionaryObject({
            NameObject("/AFRelationship"): NameObject("/Data"),
            NameObject("/Desc"): createStringObject("Factur-X Invoice"),
            NameObject("/Type"): NameObject("/Filespec"),
            NameObject("/F"): fname_obj,
            NameObject("/EF"): ef_dict,
            NameObject("/UF"): fname_obj,
            })
        filespec_obj = self._addObject(filespec_dict)
        name_arrayobj_cdict = {fname_obj: filespec_obj}
        
        # TODO: add back additional attachments?
        logger.debug('name_arrayobj_cdict=%s', name_arrayobj_cdict)
        name_arrayobj_content_sort = list(
            sorted(name_arrayobj_cdict.items(), key=lambda x: x[0]))
        logger.debug('name_arrayobj_content_sort=%s', name_arrayobj_content_sort)
        name_arrayobj_content_final = []
        af_list = []
        for (fname_obj, filespec_obj) in name_arrayobj_content_sort:
            name_arrayobj_content_final += [fname_obj, filespec_obj]
            af_list.append(filespec_obj)
        embedded_files_names_dict = DictionaryObject({
            NameObject("/Names"): ArrayObject(name_arrayobj_content_final),
            })
        
        # Then create the entry for the root, as it needs a
        # reference to the Filespec
        embedded_files_dict = DictionaryObject({
            NameObject("/EmbeddedFiles"): embedded_files_names_dict,
            })
        res_output_intents = []
        logger.debug('output_intents=%s', output_intents)
        for output_intent_dict, dest_output_profile_dict in output_intents:
            dest_output_profile_obj = self._addObject(
                dest_output_profile_dict)
            # TODO detect if there are no other objects in output_intent_dest_obj
            # than /DestOutputProfile
            output_intent_dict.update({
                NameObject("/DestOutputProfile"): dest_output_profile_obj,
                })
            output_intent_obj = self._addObject(output_intent_dict)
            res_output_intents.append(output_intent_obj)
        
        # Update the root
        xmp_level_str = self.factx.flavor.details['levels'][self.factx.flavor.level]['xmp_str']
        xmp_template = self.factx.flavor.get_xmp_xml()
        metadata_xml_str = _prepare_pdf_metadata_xml(xmp_level_str, xmp_filename, xmp_template, pdf_metadata)
        metadata_file_entry = DecodedStreamObject()
        metadata_file_entry.setData(metadata_xml_str)
        metadata_file_entry.update({
            NameObject('/Subtype'): NameObject('/XML'),
            NameObject('/Type'): NameObject('/Metadata'),
            })
        metadata_obj = self._addObject(metadata_file_entry)
        af_value_obj = self._addObject(ArrayObject(af_list))
        self._root_object.update({
            NameObject("/AF"): af_value_obj,
            NameObject("/Metadata"): metadata_obj,
            NameObject("/Names"): embedded_files_dict,
            # show attachments when opening PDF
            NameObject("/PageMode"): NameObject("/UseAttachments"),
            })
        logger.debug('res_output_intents=%s', res_output_intents)
        if res_output_intents:
            self._root_object.update({
                NameObject("/OutputIntents"): ArrayObject(res_output_intents),
            })
        metadata_txt_dict = _prepare_pdf_metadata_txt(pdf_metadata)
        self.addMetadata(metadata_txt_dict)



def _get_metadata_timestamp():
    now_dt = datetime.now()
    # example format : 2014-07-25T14:01:22+02:00
    meta_date = now_dt.strftime('%Y-%m-%dT%H:%M:%S+00:00')
    return meta_date

def _base_info2pdf_metadata(base_info):
    if base_info['doc_type'] == '381':
        doc_type_name = u'Refund'
    else:
        doc_type_name = u'Invoice'
    date_str = datetime.strftime(base_info['date'], '%Y-%m-%d')
    title = '%s: %s %s' % (
        base_info['seller'], doc_type_name, base_info['number'])
    subject = 'Factur-X %s %s dated %s issued by %s' % (
        doc_type_name, base_info['number'], date_str, base_info['seller'])
    pdf_metadata = {
        'author': base_info['seller'],
        'keywords': u'%s, Factur-X' % doc_type_name,
        'title': title,
        'subject': subject,
        }
    logger.debug('Converted base_info to pdf_metadata: %s', pdf_metadata)
    return pdf_metadata


def _prepare_pdf_metadata_txt(pdf_metadata):
    pdf_date = _get_pdf_timestamp()
    info_dict = {
        '/Author': pdf_metadata.get('author', ''),
        '/CreationDate': pdf_date,
        '/Creator':
        u'factur-x Python lib v%s by Alexis de Lattre' % __version__,
        '/Keywords': pdf_metadata.get('keywords', ''),
        '/ModDate': pdf_date,
        '/Subject': pdf_metadata.get('subject', ''),
        '/Title': pdf_metadata.get('title', ''),
        }
    return info_dict


def _prepare_pdf_metadata_xml(xmp_level_str, xmp_filename, facturx_ext_schema_root, pdf_metadata):
    nsmap_x = {'x': 'adobe:ns:meta/'}
    nsmap_rdf = {'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'}
    nsmap_dc = {'dc': 'http://purl.org/dc/elements/1.1/'}
    nsmap_pdf = {'pdf': 'http://ns.adobe.com/pdf/1.3/'}
    nsmap_xmp = {'xmp': 'http://ns.adobe.com/xap/1.0/'}
    nsmap_pdfaid = {'pdfaid': 'http://www.aiim.org/pdfa/ns/id/'}
    nsmap_fx = {
        'fx': 'urn:factur-x:pdfa:CrossIndustryDocument:invoice:1p0#'}
    ns_x = '{%s}' % nsmap_x['x']
    ns_dc = '{%s}' % nsmap_dc['dc']
    ns_rdf = '{%s}' % nsmap_rdf['rdf']
    ns_pdf = '{%s}' % nsmap_pdf['pdf']
    ns_xmp = '{%s}' % nsmap_xmp['xmp']
    ns_pdfaid = '{%s}' % nsmap_pdfaid['pdfaid']
    ns_fx = '{%s}' % nsmap_fx['fx']
    ns_xml = '{http://www.w3.org/XML/1998/namespace}'

    root = etree.Element(ns_x + 'xmpmeta', nsmap=nsmap_x)
    rdf = etree.SubElement(
        root, ns_rdf + 'RDF', nsmap=nsmap_rdf)
    desc_pdfaid = etree.SubElement(
        rdf, ns_rdf + 'Description', nsmap=nsmap_pdfaid)
    desc_pdfaid.set(ns_rdf + 'about', '')
    etree.SubElement(
        desc_pdfaid, ns_pdfaid + 'part').text = '3'
    etree.SubElement(
        desc_pdfaid, ns_pdfaid + 'conformance').text = 'B'
    desc_dc = etree.SubElement(
        rdf, ns_rdf + 'Description', nsmap=nsmap_dc)
    desc_dc.set(ns_rdf + 'about', '')
    dc_title = etree.SubElement(desc_dc, ns_dc + 'title')
    dc_title_alt = etree.SubElement(dc_title, ns_rdf + 'Alt')
    dc_title_alt_li = etree.SubElement(
        dc_title_alt, ns_rdf + 'li')
    dc_title_alt_li.text = pdf_metadata.get('title', '')
    dc_title_alt_li.set(ns_xml + 'lang', 'x-default')
    dc_creator = etree.SubElement(desc_dc, ns_dc + 'creator')
    dc_creator_seq = etree.SubElement(dc_creator, ns_rdf + 'Seq')
    etree.SubElement(
        dc_creator_seq, ns_rdf + 'li').text = pdf_metadata.get('author', '')
    dc_desc = etree.SubElement(desc_dc, ns_dc + 'description')
    dc_desc_alt = etree.SubElement(dc_desc, ns_rdf + 'Alt')
    dc_desc_alt_li = etree.SubElement(
        dc_desc_alt, ns_rdf + 'li')
    dc_desc_alt_li.text = pdf_metadata.get('subject', '')
    dc_desc_alt_li.set(ns_xml + 'lang', 'x-default')
    desc_adobe = etree.SubElement(
        rdf, ns_rdf + 'Description', nsmap=nsmap_pdf)
    desc_adobe.set(ns_rdf + 'about', '')
    producer = etree.SubElement(
        desc_adobe, ns_pdf + 'Producer')
    producer.text = 'PyPDF2'
    desc_xmp = etree.SubElement(
        rdf, ns_rdf + 'Description', nsmap=nsmap_xmp)
    desc_xmp.set(ns_rdf + 'about', '')
    creator = etree.SubElement(
        desc_xmp, ns_xmp + 'CreatorTool')
    creator.text = 'factur-x python lib v%s by Alexis de Lattre' % __version__
    timestamp = _get_metadata_timestamp()
    etree.SubElement(desc_xmp, ns_xmp + 'CreateDate').text = timestamp
    etree.SubElement(desc_xmp, ns_xmp + 'ModifyDate').text = timestamp

    # The Factur-X extension schema must be embedded into each PDF document
    facturx_ext_schema_desc_xpath = facturx_ext_schema_root.xpath(
        '//rdf:Description', namespaces=nsmap_rdf)
    rdf.append(facturx_ext_schema_desc_xpath[1])
    # Now is the Factur-X description tag
    facturx_desc = etree.SubElement(
        rdf, ns_rdf + 'Description', nsmap=nsmap_fx)
    facturx_desc.set(ns_rdf + 'about', '')
    facturx_desc.set(
        ns_fx + 'ConformanceLevel', xmp_level_str)
    facturx_desc.set(ns_fx + 'DocumentFileName', xmp_filename)
    facturx_desc.set(ns_fx + 'DocumentType', 'INVOICE')
    facturx_desc.set(ns_fx + 'Version', '1.0')

    # TODO: should be UTF-16be ??
    xml_str = etree.tostring(
        root, pretty_print=True, encoding="UTF-8", xml_declaration=False)
    head = u'<?xpacket begin="\ufeff" id="W5M0MpCehiHzreSzNTczkc9d"?>'.encode(
        'utf-8')
    tail = u'<?xpacket end="w"?>'.encode('utf-8')
    xml_final_str = head + xml_str + tail
    logger.debug('metadata XML:')
    # logger.debug(xml_final_str.decode())
    return xml_final_str


# def createByteObject(string):
#    string_to_encode = u'\ufeff' + string
#    x = string_to_encode.encode('utf-16be')
#    return ByteStringObject(x)


def _filespec_additional_attachments(
        pdf_filestream, name_arrayobj_cdict, file_dict, file_bin):
    filename = file_dict['filename']
    logger.debug('_filespec_additional_attachments filename=%s', filename)
    mod_date_pdf = _get_pdf_timestamp(file_dict['mod_date'])
    md5sum = hashlib.md5(file_bin).hexdigest()
    md5sum_obj = createStringObject(md5sum)
    params_dict = DictionaryObject({
        NameObject('/CheckSum'): md5sum_obj,
        NameObject('/ModDate'): createStringObject(mod_date_pdf),
        NameObject('/Size'): NameObject(str(len(file_bin))),
        })
    file_entry = DecodedStreamObject()
    file_entry.setData(file_bin)
    file_mimetype = mimetypes.guess_type(filename)[0]
    if not file_mimetype:
        file_mimetype = 'application/octet-stream'
    file_mimetype_insert = '/' + file_mimetype.replace('/', '#2f')
    file_entry.update({
        NameObject("/Type"): NameObject("/EmbeddedFile"),
        NameObject("/Params"): params_dict,
        NameObject("/Subtype"): NameObject(file_mimetype_insert),
        })
    file_entry_obj = pdf_filestream._addObject(file_entry)
    ef_dict = DictionaryObject({
        NameObject("/F"): file_entry_obj,
        })
    fname_obj = createStringObject(filename)
    filespec_dict = DictionaryObject({
        NameObject("/AFRelationship"): NameObject("/Unspecified"),
        NameObject("/Desc"): createStringObject(file_dict.get('desc', '')),
        NameObject("/Type"): NameObject("/Filespec"),
        NameObject("/F"): fname_obj,
        NameObject("/EF"): ef_dict,
        NameObject("/UF"): fname_obj,
        })
    filespec_obj = pdf_filestream._addObject(filespec_dict)
    name_arrayobj_cdict[fname_obj] = filespec_obj

# moved to FacturXPDFWriter
def _facturx_update_metadata_add_attachment(
        pdf_filestream, facturx_xml_str, pdf_metadata, facturx_level,
        output_intents=[], additional_attachments={}):
    '''This method is inspired from the code of the addAttachment()
    method of the PyPDF2 lib'''
    # The entry for the file
    md5sum = hashlib.md5(facturx_xml_str).hexdigest()
    md5sum_obj = createStringObject(md5sum)
    params_dict = DictionaryObject({
        NameObject('/CheckSum'): md5sum_obj,
        NameObject('/ModDate'): createStringObject(_get_pdf_timestamp()),
        NameObject('/Size'): NameObject(str(len(facturx_xml_str))),
        })
    file_entry = DecodedStreamObject()
    file_entry.setData(facturx_xml_str)  # here we integrate the file itself
    file_entry.update({
        NameObject("/Type"): NameObject("/EmbeddedFile"),
        NameObject("/Params"): params_dict,
        # 2F is '/' in hexadecimal
        NameObject("/Subtype"): NameObject("/text#2Fxml"),
        })
    file_entry_obj = pdf_filestream._addObject(file_entry)
    # The Filespec entry
    ef_dict = DictionaryObject({
        NameObject("/F"): file_entry_obj,
        NameObject('/UF'): file_entry_obj,
        })

    fname_obj = createStringObject(FACTURX_FILENAME)
    filespec_dict = DictionaryObject({
        NameObject("/AFRelationship"): NameObject("/Data"),
        NameObject("/Desc"): createStringObject("Factur-X Invoice"),
        NameObject("/Type"): NameObject("/Filespec"),
        NameObject("/F"): fname_obj,
        NameObject("/EF"): ef_dict,
        NameObject("/UF"): fname_obj,
        })
    filespec_obj = pdf_filestream._addObject(filespec_dict)
    name_arrayobj_cdict = {fname_obj: filespec_obj}
    for attach_bin, attach_dict in additional_attachments.items():
        _filespec_additional_attachments(
            pdf_filestream, name_arrayobj_cdict, attach_dict, attach_bin)
    logger.debug('name_arrayobj_cdict=%s', name_arrayobj_cdict)
    name_arrayobj_content_sort = list(
        sorted(name_arrayobj_cdict.items(), key=lambda x: x[0]))
    logger.debug('name_arrayobj_content_sort=%s', name_arrayobj_content_sort)
    name_arrayobj_content_final = []
    af_list = []
    for (fname_obj, filespec_obj) in name_arrayobj_content_sort:
        name_arrayobj_content_final += [fname_obj, filespec_obj]
        af_list.append(filespec_obj)
    embedded_files_names_dict = DictionaryObject({
        NameObject("/Names"): ArrayObject(name_arrayobj_content_final),
        })
    
    # Then create the entry for the root, as it needs a
    # reference to the Filespec
    embedded_files_dict = DictionaryObject({
        NameObject("/EmbeddedFiles"): embedded_files_names_dict,
        })
    res_output_intents = []
    logger.debug('output_intents=%s', output_intents)
    for output_intent_dict, dest_output_profile_dict in output_intents:
        dest_output_profile_obj = pdf_filestream._addObject(
            dest_output_profile_dict)
        # TODO detect if there are no other objects in output_intent_dest_obj
        # than /DestOutputProfile
        output_intent_dict.update({
            NameObject("/DestOutputProfile"): dest_output_profile_obj,
            })
        output_intent_obj = pdf_filestream._addObject(output_intent_dict)
        res_output_intents.append(output_intent_obj)
    
    # Update the root
    metadata_xml_str = _prepare_pdf_metadata_xml(facturx_level, pdf_metadata)
    metadata_file_entry = DecodedStreamObject()
    metadata_file_entry.setData(metadata_xml_str)
    metadata_file_entry.update({
        NameObject('/Subtype'): NameObject('/XML'),
        NameObject('/Type'): NameObject('/Metadata'),
        })
    metadata_obj = pdf_filestream._addObject(metadata_file_entry)
    af_value_obj = pdf_filestream._addObject(ArrayObject(af_list))
    pdf_filestream._root_object.update({
        NameObject("/AF"): af_value_obj,
        NameObject("/Metadata"): metadata_obj,
        NameObject("/Names"): embedded_files_dict,
        # show attachments when opening PDF
        NameObject("/PageMode"): NameObject("/UseAttachments"),
        })
    logger.debug('res_output_intents=%s', res_output_intents)
    if res_output_intents:
        pdf_filestream._root_object.update({
            NameObject("/OutputIntents"): ArrayObject(res_output_intents),
        })
    metadata_txt_dict = _prepare_pdf_metadata_txt(pdf_metadata)
    pdf_filestream.addMetadata(metadata_txt_dict)


def _extract_base_info(facturx_xml_etree):
    namespaces = facturx_xml_etree.nsmap
    date_xpath = facturx_xml_etree.xpath(
        '//rsm:ExchangedDocument/ram:IssueDateTime/udt:DateTimeString',
        namespaces=namespaces)
    date = date_xpath[0].text
    date_dt = datetime.strptime(date, '%Y%m%d')
    inv_num_xpath = facturx_xml_etree.xpath(
        '//rsm:ExchangedDocument/ram:ID', namespaces=namespaces)
    inv_num = inv_num_xpath[0].text
    seller_xpath = facturx_xml_etree.xpath(
        '//ram:ApplicableHeaderTradeAgreement/ram:SellerTradeParty/ram:Name',
        namespaces=namespaces)
    seller = seller_xpath[0].text
    doc_type_xpath = facturx_xml_etree.xpath(
        '//rsm:ExchangedDocument/ram:TypeCode', namespaces=namespaces)
    doc_type = doc_type_xpath[0].text
    base_info = {
        'seller': seller,
        'number': inv_num,
        'date': date_dt,
        'doc_type': doc_type,
        }
    logger.debug('Extraction of base_info: %s', base_info)
    return base_info


def _base_info2pdf_metadata(base_info):
    if base_info['doc_type'] == '381':
        doc_type_name = u'Refund'
    else:
        doc_type_name = u'Invoice'
    date_str = datetime.strftime(base_info['date'], '%Y-%m-%d')
    title = '%s: %s %s' % (
        base_info['seller'], doc_type_name, base_info['number'])
    subject = 'Factur-X %s %s dated %s issued by %s' % (
        doc_type_name, base_info['number'], date_str, base_info['seller'])
    pdf_metadata = {
        'author': base_info['seller'],
        'keywords': u'%s, Factur-X' % doc_type_name,
        'title': title,
        'subject': subject,
        }
    logger.debug('Converted base_info to pdf_metadata: %s', pdf_metadata)
    return pdf_metadata


def _get_original_output_intents(original_pdf):
    output_intents = []
    try:
        pdf_root = original_pdf.trailer['/Root']
        ori_output_intents = pdf_root['/OutputIntents']
        logger.debug('output_intents_list=%s', ori_output_intents)
        for ori_output_intent in ori_output_intents:
            ori_output_intent_dict = ori_output_intent.getObject()
            logger.debug('ori_output_intents_dict=%s', ori_output_intent_dict)
            dest_output_profile_dict =\
                ori_output_intent_dict['/DestOutputProfile'].getObject()
            output_intents.append(
                (ori_output_intent_dict, dest_output_profile_dict))
    except:
        pass
    return output_intents

def _get_pdf_timestamp(date=None):
    if date is None:
        date = datetime.now()
    # example date format: "D:20141006161354+02'00'"
    pdf_date = date.strftime("D:%Y%m%d%H%M%S+00'00'")
    return pdf_date