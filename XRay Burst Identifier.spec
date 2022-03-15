# -*- mode: python ; coding: utf-8 -*-
"""
This spec file is used by pyinstaller to create executable files.
"""
# IMPORTANT : Please run the build process after `cd`ing into the project directory
# Do not run from some other directory (or without activating the venv)

import os, sys
print(os.getcwd())

block_cipher = None


a = Analysis(['app.py'],
             pathex=[os.path.abspath(os.getcwd())],
             binaries=[],
             datas=[
                 ('templates','templates'),
                 ('static','static'),
                 ('uploads','uploads'),
                 ('fileparsers','fileparsers'),
                 ('.env','.'),
             ],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[
                 'matplotlib','pandas','IPython','jupyter',
             ],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

if 'darwin' in sys.platform :
    iconfile = 'static/sun.icns'
elif 'win' in sys.platform:
    iconfile = 'static/sun.ico'
else :
    iconfile = None

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts, 
          [],
          exclude_binaries=True,
          name='XRay Burst Identifier',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None , icon=iconfile)
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='XRay Burst Identifier')
