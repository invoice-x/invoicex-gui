#!/usr/bin/python3
# -*- coding: utf-8 -*-


import sys
from os.path import expanduser

from PyQt5.QtWidgets import (QMainWindow, QTextEdit, QAction, QApplication,
                            QFileDialog)
from PyQt5.QtCore import QDir


class InvoiceX(QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        self.initUI()
        
        
    def initUI(self):

        exitAct = QAction('Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(self.close)

        openFile = QAction('Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open new File')
        openFile.triggered.connect(self.showFileDialog)

        extractFields = QAction('Extract Fields', self)
        extractFields.setStatusTip('Extract Fields from PDF and add to XML')
        extractFields.triggered.connect(self.extractFromPDF)

        jsonFormat = QAction('JSON', self)
        jsonFormat.setStatusTip('Export file to JSON')
        xmlFormat = QAction('XML', self)
        xmlFormat.setStatusTip('Export file to XML')
        ymlFormat = QAction('YML', self)
        ymlFormat.setStatusTip('Export file to YML')

        validateMetadata = QAction('Validate', self)
        validateMetadata.setStatusTip('Validate XML')

        addMetadata = QAction('Add Metadata', self)
        addMetadata.setStatusTip('Add metadata to PDF')

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        # fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFile)
        fileMenu.addAction(exitAct)

        commandMenu = menubar.addMenu('&Command')
        
        exportMetadata = commandMenu.addMenu('&Export Metadata')
        exportMetadata.addAction(jsonFormat)
        exportMetadata.addAction(xmlFormat)
        exportMetadata.addAction(ymlFormat)
        
        commandMenu.addAction(validateMetadata)
        commandMenu.addAction(addMetadata)
        commandMenu.addAction(extractFields)

        helpMenu = menubar.addMenu('&Help')


        # toolbar = self.addToolBar('Exit')
        # toolbar.addAction(exitAct)
        
        self.setGeometry(300, 300, 550, 650)
        self.setWindowTitle('Invoice-X')    
        self.show()

    def showFileDialog(self):

        fname = QFileDialog.getOpenFileNames(self, 'Open file', expanduser("~"), "pdf (*.pdf);; All Files (*)")
        
        if fname[0]:
            print(str(fname[0][0]))
            # self.file_selected.setText(str(fname[0][0]))
            # self.file_names = fname[0]

    def extractFromPDF(self):
        pass
        
        
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    invoicex = InvoiceX()
    sys.exit(app.exec_())
