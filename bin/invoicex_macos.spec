# -*- mode: python -*-

block_cipher = None


a = Analysis(['../main.py'],
             pathex=['/home/duskybomb/projects/invoicex-gui'],
             binaries=[],
             datas=[('en.py', 'dateparser/data/date_translation_data/'),
             ('_strptime.py', '.'),('../invoicex/icons/*.png','invoicex/icons/'),
             ('../invoicex/facturx/flavors/*.yml', 'invoicex/facturx/flavors/'),
             ('../invoicex/facturx/flavors/factur-x/xml/*.xml', 'invoicex/facturx/flavors/factur-x/xml/'),
             ('../invoicex/facturx/flavors/factur-x/xsd/*.xsd', 'invoicex/facturx/flavors/factur-x/xsd/'),
             ('../invoicex/facturx/flavors/factur-x/xmp/*.xmp', 'invoicex/facturx/flavors/factur-x/xmp/'),
             ('../invoicex/facturx/flavors/zugferd/xml/*.xml', 'invoicex/facturx/flavors/zugferd/xml/'),
             ('../invoicex/facturx/flavors/zugferd/xsd/*.xsd', 'invoicex/facturx/flavors/zugferd/xsd/'),
             ('../invoicex/facturx/flavors/zugferd/xmp/*.xmp', 'invoicex/facturx/flavors/zugferd/xmp/'),
             ('templates/com/*.yml','invoice2data/extract/templates/com/'),
             ('templates/de/*.yml','invoice2data/extract/templates/de/'),
             ('templates/es/*.yml','invoice2data/extract/templates/es/'),
             ('templates/fr/*.yml','invoice2data/extract/templates/fr/'),
             ('templates/nl/*.yml','invoice2data/extract/templates/nl/'),
             ('templates/ch/*.yml','invoice2data/extract/templates/ch/')],
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
          console=False , icon='invoicex/icons/logo.ico')
