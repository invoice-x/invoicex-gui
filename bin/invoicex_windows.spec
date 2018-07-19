# -*- mode: python -*-

block_cipher = None


a = Analysis(['..\\main.py'],
             pathex=['D:\\GSoC\\invoicex-gui'],
             binaries=[],
             datas=[('..\\venv\\Lib\\site-packages\\dateparser\\data\\date_translation_data\\en.py', 'dateparser\\data\\date_translation_data\\'),
             ('..\\_strptime.py', '.'),('..\\invoicex\\icons\\*.png','invoicex\\icons\\'),
             ('..\\invoicex\\facturx\\flavors\\*.yml', 'invoicex\\facturx\\flavors\\'),
             ('..\\invoicex\\facturx\\flavors\\factur-x\\xml\\*.xml', 'invoicex\\facturx\\flavors\\factur-x\\xml\\'),
             ('..\\invoicex\\facturx\\flavors\\factur-x\\xsd\\*.xsd', 'invoicex\\facturx\\flavors\\factur-x\\xsd\\'),
             ('..\\invoicex\\facturx\\flavors\\factur-x\\xmp\\*.xmp', 'invoicex\\facturx\\flavors\\factur-x\\xmp\\'),
             ('..\\invoicex\\facturx\\flavors\\zugferd\\xml\\*.xml', 'invoicex\\facturx\\flavors\\zugferd\\xml\\'),
             ('..\\invoicex\\facturx\\flavors\\zugferd\\xsd\\*.xsd', 'invoicex\\facturx\\flavors\\zugferd\\xsd\\'),
             ('..\\invoicex\\facturx\\flavors\\zugferd\\xmp\\*.xmp', 'invoicex\\facturx\\flavors\\zugferd\\xmp\\'),
             ('..\\venv\\Lib\\site-packages\\invoice2data\\extract\\templates\\com\\*.yml','invoice2data\\extract\\templates\\com\\'),
             ('..\\venv\\Lib\\site-packages\\invoice2data\\extract\\templates\\de\\*.yml','invoice2data\\extract\\templates\\de\\'),
             ('..\\venv\\Lib\\site-packages\\invoice2data\\extract\\templates\\es\\*.yml','invoice2data\\extract\\templates\\es\\'),
             ('..\\venv\\Lib\\site-packages\\invoice2data\\extract\\templates\\fr\\*.yml','invoice2data\\extract\\templates\\fr\\'),
             ('..\\venv\\Lib\\site-packages\\invoice2data\\extract\\templates\\nl\\*.yml','invoice2data\\extract\\templates\\nl\\'),
             ('..\\venv\\Lib\\site-packages\\invoice2data\\extract\\templates\\ch\\*.yml','invoice2data\\extract\\templates\\ch\\')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='Invoice-X GUI',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True , icon='invoicex\\icons\\logo.ico')
