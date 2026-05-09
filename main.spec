# -*- mode: python ; coding: utf-8 -*-

import os
import sys

block_cipher = None

def collect_tree(src_root, dst_root):
    files = []
    if not os.path.isdir(src_root):
        return files
    for root, _, names in os.walk(src_root):
        rel_dir = os.path.relpath(root, src_root)
        dst_dir = dst_root if rel_dir == '.' else os.path.join(dst_root, rel_dir)
        for name in names:
            files.append((os.path.join(root, name), dst_dir))
    return files

credential_datas = [('googlecredential.py', '.')] if os.path.exists('googlecredential.py') else []
credential_hiddenimports = ['googlecredential'] if os.path.exists('googlecredential.py') else []
tcl_root = os.path.join(sys.base_prefix, 'tcl')
tkinter_datas = []
tkinter_binaries = []
if os.path.exists(tcl_root):
    os.environ['TCL_LIBRARY'] = os.path.join(tcl_root, 'tcl8.6')
    os.environ['TK_LIBRARY'] = os.path.join(tcl_root, 'tk8.6')
    tkinter_datas += collect_tree(os.path.join(tcl_root, 'tcl8.6'), '_tcl_data')
    tkinter_datas += collect_tree(os.path.join(tcl_root, 'tk8.6'), '_tk_data')

dll_root = os.path.join(sys.base_prefix, 'DLLs')
for name in ['_tkinter.pyd', 'tcl86t.dll', 'tk86t.dll']:
    path = os.path.join(dll_root, name)
    if os.path.exists(path):
        tkinter_binaries.append((path, '.'))


a = Analysis(['main.py'],
             pathex=['.'],
             binaries=tkinter_binaries,
             datas=credential_datas + tkinter_datas,
             hiddenimports=[
                 'googleapiclient',
                 'googleapiclient.discovery',
                 'httplib2',
                 'oauth2client',
                 '_tkinter',
                 'tkinter',
                 'tkinter.scrolledtext',
             ] + credential_hiddenimports,
             hookspath=['hooks'],
             runtime_hooks=['hooks/rthook_tkinter.py'],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='pomecalsync',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False )
