from ..invoicex import InvoiceX
import unittest
import os
from PyQt5.QtWidgets import QApplication
import sys
import shutil


class TestMainWindow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app = QApplication(sys.argv)
        cls.widget = InvoiceX()
        test_file = os.path.join(os.path.dirname(__file__),
                                 'sample_invoice/Facture_FR_BASIC.pdf')
        cls.widget.fileName = [test_file]
        cls.widget.load_pdf_file()

    # @classmethod
    # def tearDown(cls):
    #     sys.exit()

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
