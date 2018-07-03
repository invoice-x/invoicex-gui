import sys
from PyQt5.QtWidgets import QApplication
from invoicex import mainWindow


def main():
    app = QApplication(sys.argv)
    window = mainWindow.InvoiceX()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
