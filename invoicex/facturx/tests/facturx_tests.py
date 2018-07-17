import os
import unittest
from facturx.facturx import *
from lxml import etree


class TestReading(unittest.TestCase):
    def discover_files(self):
        self.test_files_dir = os.path.join(os.path.dirname(__file__), 'sample_invoices')
        self.test_files = os.listdir(self.test_files_dir)

    def test_from_file(self):
        self.discover_files()
        for file in self.test_files:
            file_path = os.path.join(self.test_files_dir, file)
            FacturX(file_path)

    # returning file path for a specific file in 'sample_invoices'
    def find_file(self, file_name):
        self.discover_files()
        for file in self.test_files:
            if file == file_name:
                file_path = os.path.join(self.test_files_dir, file)
                return file_path

    # def test_input_error(self):
    #     with self.assertRaises(TypeError) as context:
    #         FacturX('non-existant.pdf')

    def test_file_without_embedded_data(self):
        file_path = self.find_file('no_embedded_data.pdf')
        self.assertEqual(FacturX(file_path)._xml_from_file(file_path), None)

    def test_file_embedded_data(self, file_name='embedded_data.pdf'):
        file_path = self.find_file(file_name)
        self.assertTrue(FacturX(file_path)._xml_from_file(file_path) is not None, "The PDF file has no embedded file")

    def test_write_pdf(self):
        file_path = self.find_file('no_embedded_data.pdf')
        factx = FacturX(file_path)
        test_file_path = os.path.join(self.test_files_dir, 'test.pdf')

        # checking if pdf file is made
        factx.write_pdf(test_file_path)
        self.assertTrue(os.path.isfile(test_file_path))
        self.discover_files()

        # checking that xml is embedded
        self.assertTrue(self.test_file_embedded_data(file_name='test.pdf') is None)

        os.remove(test_file_path)

    def test_write_xml(self):
        compare_file_dir = os.path.join(os.path.dirname(__file__), 'compare')
        expected_file_path = os.path.join(compare_file_dir, 'no_embedded_data.xml')
        test_file_path = os.path.join(compare_file_dir, 'test.xml')

        factx = FacturX(self.find_file('no_embedded_data.pdf'))
        factx.write_xml(test_file_path)
        self.assertTrue(os.path.isfile(test_file_path))

        with open(expected_file_path, 'r') as expected_file, open(test_file_path, 'r') as test_file:
            parser = etree.XMLParser(remove_blank_text=True)
            expected_file_root = etree.XML(expected_file.read(), parser)
            expected_file_str = etree.tostring(expected_file_root)

            test_file_root = etree.XML(test_file.read(), parser)
            test_file_str = etree.tostring(test_file_root)

        self.assertTrue(expected_file_str == test_file_str, "Files don't match")
        os.remove(test_file_path)


def main():
    unittest.main()


if __name__ == '__main__':
    main()
