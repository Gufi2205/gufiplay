# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['Descargador.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('Descargador.py', '.'),
        ('ffmpeg/bin/ffmpeg.exe', 'ffmpeg/bin'),
        ('ffmpeg/bin/ffplay.exe', 'ffmpeg/bin'),
        ('ffmpeg/bin/ffprobe.exe', 'ffmpeg/bin'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Descargador',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
