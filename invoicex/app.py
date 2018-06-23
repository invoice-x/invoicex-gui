import sys
from PyQt5.QtWidgets import QApplication
from invoicex.ui import mainWindow


QApplication.setApplicationName('InvoiceX')
QApplication.setApplicationVersion('0.1')

app = QApplication(sys.argv)
invoicex = mainWindow.InvoiceX()
