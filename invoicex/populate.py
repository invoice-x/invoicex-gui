from PyQt5.QtWidgets import (QWidget, QPushButton, QGridLayout, QFileDialog,
                             QLabel, QLineEdit, QMessageBox, QCheckBox)
from PyQt5.QtGui import QIcon, QFont
import configparser
from invoice2data.main import main, create_parser
import json


class PopulateFieldClass(QWidget):
    def __init__(self, gui, factx, fieldsDict, metadataDict):
        super().__init__()
        self.gui = gui
        self.fDict = fieldsDict
        self.mDict = metadataDict
        self.factx = factx
        self.customTemplateFolderName = None
        self.init_ui()

    def init_ui(self):
        """Setup layout to add default field values"""
        layout = QGridLayout()
        i = 3
        customTemplate = QPushButton('Custom Template')
        customTemplate.clicked.connect(self.customTemplateDialog)
        layout.addWidget(customTemplate, 0, 0)

        self.excludeDefaultFolder = QCheckBox(
            'Exclude default template folder', self)
        layout.addWidget(self.excludeDefaultFolder, 1, 1)

        self.customTemplateLineEdit = QLineEdit()
        self.customTemplateLineEdit.setDisabled(True)
        layout.addWidget(self.customTemplateLineEdit, 0, 1)

        labelBlank = QLabel(" ")
        layout.addWidget(labelBlank, 1, 0)

        labelTitle = QLabel("Add Default Values")
        labelTitle.setFont(QFont("Add Default Values", weight=QFont.Bold))
        layout.addWidget(labelTitle, 2, 0)
        self.fieldsKeyList = []
        self.fieldsValueList = []
        for key in sorted(self.fDict):
            i += 1
            fKey = QLabel(self.mDict[key])
            fValue = QLineEdit()
            fValue.setText("")
            if self.fDict[key] == "Field Not Specified" or key[:4] == "date":
                fValue.setEnabled(False)
            else:
                self.fieldsKeyList.append(key)
                self.fieldsValueList.append(fValue)
            layout.addWidget(fKey, i, 0)
            layout.addWidget(fValue, i, 1)

        i += 1
        saveButton = QPushButton('Apply')
        saveButton.clicked.connect(self.call_invoice2data)
        resetButton = QPushButton('Discard')
        resetButton.clicked.connect(self.resetLabel)
        layout.addWidget(resetButton, i, 0)
        layout.addWidget(saveButton, i, 1)

        self.setLayout(layout)
        self.move(300, 150)
        self.setWindowTitle('Edit Fields')
        self.setWindowIcon(QIcon('icons/logo.png'))
        self.show()

    def customTemplateDialog(self):
        """Dialog to select location of custom Template Folder"""
        self.customTemplateFolderName = QFileDialog.getExistingDirectory(
            self, "Select Custom Template Folder")
        if self.customTemplateFolderName:
            self.customTemplateLineEdit.setText(self.customTemplateFolderName)

    def call_invoice2data(self):
        """Invoke invoice2data"""
        if self.excludeDefaultFolder.isChecked() and \
                self.customTemplateFolderName is None:
            QMessageBox.critical(self, 'Error',
                                 "Select a custom template first",
                                 QMessageBox.Ok)
        else:
            config = configparser.ConfigParser()
            config['CUSTOM'] = {}
            for key, value in zip(self.fieldsKeyList, self.fieldsValueList):
                if value.text() is not "":
                    config['CUSTOM'][key] = value.text()
            with open('.load/default.cfg', 'w') as configfile:
                config.write(configfile)
            populate_using_invoice2data(self,
                                        self.excludeDefaultFolder.isChecked(),
                                        self.customTemplateFolderName,
                                        self.fDict,
                                        self.gui,
                                        self.factx)
            self.close()

    def resetLabel(self):
        self.close()


class populate_using_invoice2data(object):
    def __init__(self, popfield, excludeDefaultFolder, templateFolder,
                 fieldDict, gui, factx):
        self.parser = create_parser()
        self.fieldValueDict = fieldDict
        self.gui = gui
        self.factx = factx
        self.popfield = popfield
        self.outputFile = '.load/invoice2data_output.json'
        self.parseList = ['--output-format',
                          'json',
                          '--output-name',
                          self.outputFile,
                          '--exclude-built-in-templates',
                          '--template-folder',
                          templateFolder,
                          self.gui.fileName[0]]
        if not excludeDefaultFolder:
            self.parseList.remove('--exclude-built-in-templates')
        if templateFolder is None:
            self.parseList.remove('--template-folder')
            self.parseList.remove(templateFolder)

        main(self.parser.parse_args(self.parseList))

        self.set_values()

    def set_values(self):
        """Set field values using invoice2data"""
        templateerror = False
        fieldMatchDict = {
            'seller': 'issuer',
            'amount_total': 'amount'
        }
        try:
            with open(self.outputFile, 'r') as json_file:
                invoiceFieldDict = json.load(json_file)
                config = configparser.RawConfigParser()
                config.read('.load/default.cfg')
                for key, value in config['CUSTOM'].items():
                    if key in fieldMatchDict:
                        invoiceFieldDict[0][fieldMatchDict[key]] = value

                    invoiceFieldDict[0][key] = value
                for key in self.fieldValueDict:
                    if key in invoiceFieldDict[0]:
                        self.fieldValueDict[key] = invoiceFieldDict[0][key]
                    if key in fieldMatchDict:
                            self.fieldValueDict[key] = \
                                invoiceFieldDict[0][fieldMatchDict[key]]
        except IndexError:
            templateerror = True
            QMessageBox.critical(self.popfield, 'Template Error',
                                 "No matching template found",
                                 QMessageBox.Ok)

        if not templateerror:
            for key, value in self.fieldValueDict.items():
                    try:
                        if key[:4] != "date":
                            if value is None:
                                self.factx[key] = "NA"
                            else:
                                self.factx[key] = str(value)
                        else:
                            pass
                    except IndexError:
                        pass

            self.gui.update_dock_fields()
