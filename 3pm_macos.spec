# -*- mode: python -*-

block_cipher = None


a = Analysis(['src/main.py'],
             pathex=['/Users/chris/3pm'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['_tkinter', 'Tkinter', 'enchant', 'twisted'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='3pm',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          console=True , icon='src/data/icon.ico')
coll = COLLECT(exe, Tree('src/'),
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               name='3pm')
app = BUNDLE(coll,
             name='3pm.app',
             icon='src/data/icon_macos.png',
             bundle_identifier=None)
