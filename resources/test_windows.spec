# -*- mode: python -*-
a = Analysis(['test.py'],
             pathex=[''],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
for d in a.datas:
    if 'pyconfig' in d[0]: 
        a.datas.remove(d)
        break
pyz = PYZ(a.pure)
exe = EXE(pyz,
	  Tree('data', prefix='data'),
          a.scripts  + [('O','','OPTION')],
          a.binaries,
          a.zipfiles,
          a.datas,
          name='test.exe',
          debug=False,
          strip=None,
          upx=True,
          console=False )
