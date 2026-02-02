# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['voice_coding.py'],
    pathex=[],
    binaries=[],
    datas=[('web', 'web')],
    hiddenimports=['cryptography', 'cryptography.x509', 'cryptography.hazmat.primitives',
                  'cryptography.hazmat.primitives.asymmetric', 'cryptography.hazmat.backends',
                  'cryptography.hazmat.primitives.serialization', 'cryptography.hazmat.primitives.hashes',
                  'cryptography.x509.oid', 'ipaddress', '_ssl', 'ssl',
                  'pyngrok', 'pyngrok.ngrok', 'yaml', '_yaml'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='VoiceCoding',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
