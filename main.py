if __name__ == '__main__':

    import sys

    from PyQt5.QtWidgets import QApplication

    from invoicex import mainWindow

    app = QApplication(sys.argv)
    window = mainWindow.InvoiceX()

    sys.exit(app.exec_())
