from ..invoicex import InvoiceX
import unittest
import os
from PyQt5.QtCore import QCoreApplication
import sys
import shutil


class TestMainWindow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app = QCoreApplication(sys.argv)
        cls.widget = InvoiceX()
        cls.widget.fileName = ['../invoice.pdf']
        cls.widget.load_pdf_file()

    def test_pdf_preview(self):
        self.assertTrue(os.path.isfile('.load/preview.jpg'),
                        "Image file of pdf was not generated")

    def test_save_as(self):
        if not os.path.isdir('temp_test_file'):
            os.mkdir('temp_test_file')
        file_path = 'temp_test_file/output.xml'
        self.widget.pdf_write_xml(file_path)
        self.assertTrue(os.path.isfile(file_path))
        shutil.rmtree('temp_test_file')


if __name__ == '__main__':
    unittest.main()
