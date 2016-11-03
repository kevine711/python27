# -*- mode: python -*-
a = Analysis(['TCPSSH_relay_server.py'],
             pathex=['C:\\python'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
a.datas += [('favicon2.ico','C:\\python\\favicon2.ico','DATA')]
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='TCP2SSH.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True , version='version.txt', icon='favicon2.ico')
