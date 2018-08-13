# -*- mode: python -*-

block_cipher = None

api_a = Analysis(
            ['api.py'],
            binaries=[],
            datas=[],
            hiddenimports=['gevent', 'flask', 'flask_cors'],
            hookspath=[],
            runtime_hooks=[],
            excludes=[],
            win_no_prefer_redirects=False,
            win_private_assemblies=False,
            cipher=block_cipher)
collect_a = Analysis(
            ['collect.py'],
            binaries=[],
            datas=[],
            hiddenimports=['win32timezone'],
            hookspath=[],
            runtime_hooks=[],
            excludes=[],
            win_no_prefer_redirects=False,
            win_private_assemblies=False,
            cipher=block_cipher)
namsd_a = Analysis(
            ['namsd.py'],
            binaries=[],
            datas=[],
            hiddenimports=['win32timezone'],
            hookspath=[],
            runtime_hooks=[],
            excludes=[],
            win_no_prefer_redirects=False,
            win_private_assemblies=False,
            cipher=block_cipher)


api_pyz = PYZ(api_a.pure, api_a.zipped_data, cipher=block_cipher)
collect_pyz = PYZ(collect_a.pure, collect_a.zipped_data, cipher=block_cipher)
namsd_pyz = PYZ(namsd_a.pure, namsd_a.zipped_data, cipher=block_cipher)


api_exe = EXE(
            api_pyz,
            api_a.scripts,
            api_a.binaries,
            api_a.zipfiles,
            api_a.datas,
            name='api',
            debug=False,
            strip=False,
            upx=True,
            runtime_tmpdir=None,
            console=True)

collect_exe = EXE(
            collect_pyz,
            collect_a.scripts,
            collect_a.binaries,
            collect_a.zipfiles,
            collect_a.datas,
            name='collect',
            debug=False,
            strip=False,
            upx=True,
            runtime_tmpdir=None,
            console=True)

namsd_exe = EXE(
            namsd_pyz,
            namsd_a.scripts,
            namsd_a.binaries,
            namsd_a.zipfiles,
            namsd_a.datas,
            name='namsd',
            debug=False,
            strip=False,
            upx=True,
            runtime_tmpdir=None,
            console=True)
