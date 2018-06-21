#!/usr/bin/python3
# -*- coding: utf-8 -*-


import sys
from os.path import expanduser

from PyQt5.QtWidgets import (QMainWindow, QTextEdit, QAction, QApplication,
                            QFileDialog, QLabel, QWidget, QDockWidget,
                            QListWidget, QHBoxLayout, QSizePolicy)
from PyQt5.QtGui import QPixmap, QColor, QIcon
from PyQt5.QtCore import Qt, QEvent

class InvoiceX(QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        self.left = 300
        self.top = 300
        self.width = 1
        self.height = 1

        self.initialLoad = 0

        self.initUI()
        
    def initUI(self):

        print()
        # StatusBar
        self.statusBar()
        self.setStatusTip('Select a PDF to get started')

        # MenuBar
        self.setMenuBar()

        # Dock View Right (Fields)
        self.fields = QDockWidget("Fields", self)
        self.fieldsWidget = QLabel(self)

        self.fields.setWidget(self.fieldsWidget)
        self.fields.setFloating(False)
        self.fields.setMinimumWidth(300)
        self.fields.setStyleSheet("QWidget { background-color: #AAB2BD}")        
        self.addDockWidget(Qt.RightDockWidgetArea, self.fields)

        # Central Widget

        # self.square = QLabel(self)
        # self.pixmap = QPixmap('image.jpg')
        # self.pixmap = self.pixmap.scaledToHeight(1000, Qt.SmoothTransformation)
        # self.square.setPixmap(self.pixmap)
        # self.square.resize(self.pixmap.width(), self.pixmap.height())
        # self.square.setStyleSheet("QWidget { background-color: #CCD1D9 }")

        # hbox = QHBoxLayout()
        # hbox.addWidget(self.square)
        # centreWidget = QWidget()
        # centreWidget.setLayout(hbox)
        # print(centreWidget.size())
        # self.pixmap = self.pixmap.scaledToHeight(centreWidget.size().height(), Qt.SmoothTransformation)
        # self.square.setPixmap(self.pixmap)
        self.square = QLabel(self)
        # self.pixmap = QPixmap('image.jpg')
        # self.square.setPixmap(self.pixmap)
        # self.square.setStyleSheet("background-image: url(image.jpg); background-repeat: no-repeat   ")
        self.square.setPixmap(QPixmap('image.jpg').scaled(300,400,Qt.KeepAspectRatio , Qt.SmoothTransformation))
        self.setCentralWidget(self.square)

        toolbar = self.addToolBar('File')
        toolbar.addAction(self.openFile)
        toolbar.addAction(self.saveFile)
        toolbar.addAction(self.validateMetadata)

        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowTitle('Invoice-X')    
        self.show()

    def setMenuBar(self):
        self.exitAct = QAction(QIcon('icons/exit.png'), 'Exit', self)
        self.exitAct.setShortcut('Ctrl+Q')
        self.exitAct.setStatusTip('Exit application')
        self.exitAct.triggered.connect(self.close)

        self.openFile = QAction(QIcon('icons/pdf.png'), 'Open', self)
        self.openFile.setShortcut('Ctrl+O')
        self.openFile.setStatusTip('Open new File')
        self.openFile.triggered.connect(self.showFileDialog)

        self.saveFile = QAction(QIcon('icons/save.png'), 'Save', self)
        self.saveFile.setShortcut('Ctrl+S')
        self.saveFile.setStatusTip('Save File as a new File')
        self.saveFile.triggered.connect(self.showSaveDialog)

        extractFields = QAction('Extract Fields', self)
        extractFields.setStatusTip('Extract Fields from PDF and add to XML')
        extractFields.triggered.connect(self.extractFromPDF)

        jsonFormat = QAction('JSON', self)
        jsonFormat.setStatusTip('Export file to JSON')
        jsonFormat.triggered.connect(lambda: self.exportFields('json'))
        
        xmlFormat = QAction('XML', self)
        xmlFormat.setStatusTip('Export file to XML')
        xmlFormat.triggered.connect(lambda: self.exportFields('xml'))
        
        ymlFormat = QAction('YML', self)
        ymlFormat.setStatusTip('Export file to YML')
        ymlFormat.triggered.connect(lambda: self.exportFields('yml'))

        self.validateMetadata = QAction(QIcon('icons/validate.png'), 'Validate', self)
        self.validateMetadata.setStatusTip('Validate XML')

        addMetadata = QAction('Add Metadata', self)
        addMetadata.setStatusTip('Add metadata to PDF')

        editFields = QAction('Edit Fields', self)
        editFields.setStatusTip('Edit Fields in XML')

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(self.openFile)
        fileMenu.addAction(self.saveFile)
        fileMenu.addAction(self.exitAct)

        commandMenu = menubar.addMenu('&Command')
        
        exportMetadata = commandMenu.addMenu('&Export Metadata')
        exportMetadata.addAction(jsonFormat)
        exportMetadata.addAction(xmlFormat)
        exportMetadata.addAction(ymlFormat)
        
        commandMenu.addAction(self.validateMetadata)
        commandMenu.addAction(editFields)
        commandMenu.addAction(addMetadata)
        commandMenu.addAction(extractFields)

        helpMenu = menubar.addMenu('&Help')

    def showFileDialog(self):

        fname = QFileDialog.getOpenFileNames(self, 'Open file', expanduser("~"), "pdf (*.pdf);; All Files (*)")
        
        if fname[0]:
            print(str(fname[0][0]))
            # self.file_selected.setText(str(fname[0][0]))
            # self.file_names = fname[0]

    def showSaveDialog(self):
        pass

    def extractFromPDF(self):
        pass

    def exportFields(self, outputformat):
        pass

    # def eventFilter(self, widget, event):
    #     if (event.type() == QEvent.Resize and
    #         widget is self.square):
    #         self.square.setPixmap(self.pixmap.scaled(
    #             self.square.width(), self.square.height(),
    #             Qt.KeepAspectRatio))
    #         return True
    #     return QMainWindow.eventFilter(self, widget, event)
    
    def resizeEvent(self, event):
        if self.initialLoad == 0:
            self.initialLoad = 1
            self.square.setPixmap(QPixmap('image.jpg').scaled(300,400,Qt.KeepAspectRatio , Qt.SmoothTransformation))
        else:
            self.square.setPixmap(QPixmap('image.jpg').scaled(self.square.size().width(),self.square.size().height(),Qt.KeepAspectRatio , Qt.SmoothTransformation))
            self.square.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Ignored)
            self.square.setAlignment(Qt.AlignCenter)
            QMainWindow.resizeEvent(self, event)

        
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    invoicex = InvoiceX()
    sys.exit(app.exec_())
