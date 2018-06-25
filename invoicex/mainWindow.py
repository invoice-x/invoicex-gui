import subprocess
import os
import sys
from distutils import spawn

from facturx import *
import json
from datetime import datetime as dt

from PyQt5.QtWidgets import (QMainWindow, QAction, QFileDialog, QLineEdit,
                             QLabel, QDockWidget, QSizePolicy, QGridLayout,
                             QScrollArea, QWidget, QMessageBox, QPushButton)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QEvent


class InvoiceX(QMainWindow):

    def __init__(self):
        super().__init__()

        self.left = 300
        self.top = 300
        self.width = 680
        self.height = 480

        self.fileLoaded = False
        self.dialog = None
        self.initUI()

    def initUI(self):

        # StatusBar

        self.statusBar()
        self.setStatusTip('Select a PDF to get started')
        self.setMenuBar()
        self.setDockViewRight()
        self.setCenterWidget()
        self.setToolBar()

        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowTitle('Invoice-X')
        self.setWindowIcon(QIcon('icons/logo.png'))
        self.show()

        if not spawn.find_executable('convert'):
            QMessageBox.critical(self, 'Import Error',
                                 "Imagemagick is not installed",
                                 QMessageBox.Ok)
            if sys.platform[:3] == 'win':
                if not spawn.find_executable('gswin32'):
                    QMessageBox.critical(self, 'Import Error',
                                         "GhostScript is not installed",
                                         QMessageBox.Ok)

    def setToolBar(self):
        toolbar = self.addToolBar('File')
        toolbar.addAction(self.openFile)
        toolbar.addAction(self.saveFile)
        toolbar.addAction(self.validateMetadata)
        toolbar.addAction(self.editFields)

    def setCenterWidget(self):
        self.square = QLabel(self)
        self.square.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self.square)

    def setDockViewRight(self):
        self.fields = QDockWidget("Fields", self)
        self.fields.installEventFilter(self)
        self.fieldsQWidget = QWidget()
        self.fieldsScrollArea = QScrollArea()
        self.fieldsScrollArea.setWidgetResizable(True)
        self.fieldsScrollArea.setWidget(self.fieldsQWidget)

        self.layout = QGridLayout()
        self.fieldsQWidget.setLayout(self.layout)

        self.fields.setWidget(self.fieldsScrollArea)
        self.fields.setFloating(False)
        self.fields.setMinimumWidth(360)
        self.fields.setStyleSheet("QWidget { background-color: #AAB2BD}")
        self.addDockWidget(Qt.RightDockWidgetArea, self.fields)

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
        self.saveFile.setStatusTip('Save File')
        self.saveFile.triggered.connect(self.saveFileDialog)

        self.saveAsFile = QAction('Save As', self)
        self.saveAsFile.setStatusTip('Save File as a new File')
        self.saveAsFile.triggered.connect(self.showSaveAsDialog)

        self.viewDock = QAction('View Dock', self, checkable=True)
        self.viewDock.setStatusTip('View Dock')
        self.viewDock.setChecked(True)
        self.viewDock.triggered.connect(self.viewDockToggle)

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

        self.validateMetadata = QAction(QIcon('icons/validate.png'),
                                        'Validate', self)
        self.validateMetadata.setStatusTip('Validate XML')
        self.validateMetadata.triggered.connect(self.validateXML)

        addMetadata = QAction('Add Metadata', self)
        addMetadata.setStatusTip('Add metadata to PDF')

        self.editFields = QAction(QIcon('icons/edit.png'), 'Edit Metadata', self)
        self.editFields.setStatusTip('Edit Metadata in XML')
        self.editFields.triggered.connect(self.editFieldsDialog)

        documentation = QAction('Documentation', self)
        documentation.setStatusTip('Open Documentation for Invoice-X')

        aboutApp = QAction('About', self)
        aboutApp.setStatusTip('Know about Invoice-X')

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(self.openFile)
        fileMenu.addAction(self.saveFile)
        fileMenu.addAction(self.saveAsFile)
        fileMenu.addAction(self.viewDock)
        fileMenu.addAction(self.exitAct)

        commandMenu = menubar.addMenu('&Command')

        exportMetadata = commandMenu.addMenu('&Export Metadata')
        exportMetadata.addAction(jsonFormat)
        exportMetadata.addAction(xmlFormat)
        exportMetadata.addAction(ymlFormat)

        commandMenu.addAction(self.validateMetadata)
        commandMenu.addAction(self.editFields)
        commandMenu.addAction(addMetadata)
        commandMenu.addAction(extractFields)

        helpMenu = menubar.addMenu('&Help')
        helpMenu.addAction(documentation)
        helpMenu.addAction(aboutApp)

    def viewDockToggle(self, state):
        if state:
            self.fields.show()
        else:
            self.fields.hide()

    def validateXML(self):
        try:
            if self.factx.is_valid():
                QMessageBox.information(self, 'Valid XML',
                                        "The XML is Valid",
                                        QMessageBox.Ok)
            else:
                QMessageBox.critical(self, 'Invalid XML',
                                     "The XML is invalid",
                                     QMessageBox.Ok)
        except AttributeError:
            QMessageBox.critical(self, 'File Not Found',
                                 "Load a PDF first",
                                 QMessageBox.Ok)

    def setPdfPreview(self):
        # print(str(fileName[0]))
        if not os.path.exists('.load'):
            os.mkdir('.load')
        if sys.platform[:3] == 'win':
            convert = ['magick', self.fileName[0], '-flatten', '.load/preview.jpg']
        else:
            convert = ['convert', '-verbose', '-density', '150', '-trim',
                       self.fileName[0], '-quality', '100', '-flatten',
                       '-sharpen', '0x1.0', '.load/preview.jpg']
        subprocess.call(convert)
        self.pdfPreview = '.load/preview.jpg'
        self.fileLoaded = True
        self.square.setPixmap(QPixmap(self.pdfPreview).scaled(self.square.size().width(), self.square.size().height(),Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def editFieldsDialog(self):
        try:
            self.dialog = EditFieldsClass(self.factx, self.fieldsDict, self.metadata_field)
            self.dialog.installEventFilter(self)
            # self.dialog.show()
        except AttributeError:
            QMessageBox.critical(self, 'File Not Found',
                                 "Load a PDF first",
                                 QMessageBox.Ok)

    def showFields(self):
        self.factx.write_json('.load/output.json')
        with open('.load/output.json') as jsonFile:
            self.fieldsDict = json.load(jsonFile)
        os.remove('.load/output.json')
        # print(self.fieldsDict)

        i = 0

        self.metadata_field = {
            'amount_tax': 'Amount Tax',
            'amount_total': 'Amount Total',
            'amount_untaxed': 'Amount Untaxed',
            'buyer': 'Buyer',
            'currency': 'Currency',
            'date': 'Date',
            'date_due': 'Date Due',
            'invoice_number': 'Invoice Number',
            'name': 'Name',
            'notes': 'Notes',
            'seller': 'Seller',
            'type': 'Type',
            'version': 'Version'
        }

        for key in sorted(self.fieldsDict):
            i += 1
            try:
                self.factx[key]
            except IndexError:
                self.fieldsDict[key] = "Field Not Specified"
            fieldKey = QLabel(self.metadata_field[key] + ": ")
            if self.fieldsDict[key] is None:
                fieldValue = QLabel("NA")
            else:
                if key[:4] == "date" and self.fieldsDict[key] != "Field Not Specified":
                    self.fieldsDict[key] = self.fieldsDict[key][:4] + "/" + self.fieldsDict[key][4:6] + "/" + self.fieldsDict[key][6:8]
                fieldValue = QLabel(self.fieldsDict[key])
            # fieldValue.setFrameShape(QFrame.Panel)
            # fieldValue.setFrameShadow(QFrame.Plain)
            # fieldValue.setLineWidth(3)
            self.layout.addWidget(fieldKey, i, 0)
            self.layout.addWidget(fieldValue, i, 1)

    def showFileDialog(self):

        self.fileName = QFileDialog.getOpenFileName(self, 'Open file',
                                                    os.path.expanduser("~"),
                                                    "pdf (*.pdf)")

        if self.fileName[0]:
            # print(fileName[0])
            self.factx = FacturX(self.fileName[0])
            self.setPdfPreview()
            self.showFields()
            self.setStatusTip("PDF is Ready")

            # self.file_selected.setText(str(fname[0][0]))
            # self.file_names = fname[0]

    def saveFileDialog(self):
        if self.fileLoaded:
            self.factx.write_pdf(self.fileName[0])
        else:
            QMessageBox.critical(self, 'File Not Found',
                                 "Load a PDF first",
                                 QMessageBox.Ok)

    def showSaveAsDialog(self):
        if self.fileLoaded:
            self.saveFileName = QFileDialog.getSaveFileName(self, 'Save file',
                                                            os.path.expanduser("~"),
                                                            "pdf (*.pdf)")
            if self.saveFileName[0]:
                self.factx.write_pdf(self.saveFileName[0])
        else:
            QMessageBox.critical(self, 'File Not Found',
                                 "Load a PDF first",
                                 QMessageBox.Ok)

    def extractFromPDF(self):
        pass

    def exportFields(self, outputformat):
        pass

    def resizeEvent(self, event):
        if self.fileLoaded:
            self.square.setPixmap(QPixmap(self.pdfPreview).scaled(self.square.size().width(),self.square.size().height(),Qt.KeepAspectRatio , Qt.SmoothTransformation))
            self.square.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Ignored)
            QMainWindow.resizeEvent(self, event)

    def eventFilter(self, source, event):
        if event.type() == QEvent.Close and source is self.fields:
            self.viewDock.setChecked(False)

        if event.type() == QEvent.Close and source is self.dialog:
            self.showFields()
        return QMainWindow.eventFilter(self, source, event)


class EditFieldsClass(QWidget, object):
    def __init__(self, factx, fieldsDict, metadataDict):
        super().__init__()
        self.fDict = fieldsDict
        self.mDict = metadataDict
        self.factx = factx
        self.initUI()

    def initUI(self):
        layout = QGridLayout()
        i = 0
        self.fieldsKeyList = []
        self.fieldsValueList = []
        for key in sorted(self.fDict):
            i += 1
            fKey = QLabel(self.mDict[key])
            fValue = QLineEdit()
            fValue.setText(self.fDict[key])
            if self.fDict[key] == "Field Not Specified":
                fValue.setEnabled(False)
            else:
                self.fieldsKeyList.append(key)
                self.fieldsValueList.append(fValue)
            layout.addWidget(fKey, i, 0)
            layout.addWidget(fValue, i, 1)

        i = i + 1
        saveButton = QPushButton('Apply')
        saveButton.clicked.connect(self.addToDock)
        resetButton = QPushButton('Discard')
        resetButton.clicked.connect(self.resetLabel)
        layout.addWidget(resetButton, i, 0)
        layout.addWidget(saveButton, i, 1)

        self.setLayout(layout)
        self.move(300, 150)
        self.setWindowTitle('Edit Fields')
        self.show()

    def addToDock(self):
        try:
            for key, value in zip(self.fieldsKeyList, self.fieldsValueList):
                if key[:4] != "date":
                    self.factx[key] = value.text()
                else:
                    self.factx[key] = dt.strptime(value.text(), '%Y/%m/%d')
            self.close()
        except ValueError:
            QMessageBox.critical(self, 'Invalid Field Value',
                                 "Invalid Field Value(s)",
                                 QMessageBox.Ok)

    def resetLabel(self):
        self.close()
