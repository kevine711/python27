# -*- mode: python -*-
a = Analysis(['gpib27.py'],
             pathex=['C:\\python\\GPIB'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
a.datas += [('favicon2.ico','C:\\python\\GPIB\\favicon2.ico','DATA')]
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='GPIB_TOOL.exe',
          debug=False,
          strip=None,
          upx=True,
          console=False , version='version.txt', icon='favicon2.ico')
