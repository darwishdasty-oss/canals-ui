# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for Hydraulic Design Studio.
Build with:
    pyinstaller hydraulic.spec --noconfirm
"""
from PyInstaller.utils.hooks import collect_data_files, collect_submodules
import sys
from pathlib import Path

block_cipher = None
HERE = Path(SPECPATH).resolve()

# Streamlit ships a couple of static/template files we need to ship too
datas = []
datas += [(str(HERE / "app.py"),            ".")]
datas += [(str(HERE / "open_channel.py"),   ".")]
datas += [(str(HERE / "structures.py"),     ".")]
datas += [(str(HERE / "earth_canal.py"),    ".")]
datas += [(str(HERE / "requirements.txt"),  ".")]
datas += collect_data_files("streamlit", include_py_files=False)

hiddenimports = []
hiddenimports += collect_submodules("streamlit")
hiddenimports += [
    "streamlit.web.cli",
    "streamlit.runtime.scriptrunner",
    "streamlit.runtime.scriptrunner.add_script_run_ctx",
    "streamlit.components.v1.components",
    "altair",
    "pyarrow",
    "git",
    "webview",
    "bottle",
    "scipy.signal",
    "scipy.integrate",
    "scipy.optimize",
    "scipy.interpolate",
    "matplotlib.backends.backend_agg",
]

a = Analysis(
    ["launcher.py"],
    pathex=[str(HERE)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter", "PyQt5", "PyQt6", "PySide2", "PySide6",
        "IPython", "jupyter", "notebook", "pytest",
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
    console=True,            # show a console window for log feedback
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,                # add icon.ico here if you have one
)
