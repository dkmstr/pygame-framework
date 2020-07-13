# -*- mode: python -*-
a = Analysis(['test.py'],
             pathex=['/Users/admin/pygame/resources'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='test',
          debug=False,
          strip=None,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name='test')
app = BUNDLE(coll,
             Tree('data', prefix='data'),
             name='test.app',
             icon=None)
