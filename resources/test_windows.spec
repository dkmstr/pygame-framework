# -*- mode: python -*-
a = Analysis(['test.py'],
             pathex=['M:\\projects\\pygame\\resources'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
	  Tree('data', prefix='data'),
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='test.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True )
