# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for the simple (browser-based) launcher.
Use this if the native-window (pywebview) build misbehaves.
Build with:
    pyinstaller hydraulic_simple.spec --noconfirm
"""
from PyInstaller.utils.hooks import collect_data_files, collect_submodules
import sys
from pathlib import Path

block_cipher = None
HERE = Path(SPECPATH).resolve()

datas = []
datas += [(str(HERE / "app.py"),            ".")]
datas += [(str(HERE / "open_channel.py"),   ".")]
datas += [(str(HERE / "structures.py"),     ".")]
datas += [(str(HERE / "earth_canal.py"),    ".")]
datas += collect_data_files("streamlit", include_py_files=False)

hiddenimports = []
hiddenimports += collect_submodules("streamlit")
hiddenimports += [
    "streamlit.web.cli",
    "streamlit.runtime.scriptrunner",
    "altair",
    "pyarrow",
    "git",
    "scipy.signal",
    "scipy.integrate",
    "scipy.optimize",
    "scipy.interpolate",
    "matplotlib.backends.backend_agg",
]

a = Analysis(
    ["launcher_simple.py"],
    pathex=[str(HERE)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter", "PyQt5", "PyQt6", "PySide2", "PySide6",
        "IPython", "jupyter", "notebook", "pytest", "webview", "bottle",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="HydraulicStudio",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
