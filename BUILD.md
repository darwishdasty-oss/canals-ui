# Building a Windows `.exe`

This project can be packaged as a single, self-contained Windows executable:
**`HydraulicStudio.exe`**. When launched, it opens its own native window (no
browser, no console window) and runs the entire app locally.

## Quick start (Windows 10/11, 64-bit)

```bat
build_windows.bat
```

That's it. After 3–5 minutes you'll find **`dist\HydraulicStudio.exe`**
(~150-250 MB). Double-click it to launch.

The script:
1. Creates a `venv` virtualenv (only on first run)
2. Installs `streamlit`, `numpy`, `scipy`, `matplotlib`, `pywebview`, `pyinstaller`
3. Runs `pyinstaller hydraulic.spec --noconfirm --clean`

## Alternative: build in the cloud (no Windows machine needed)

A GitHub Actions workflow is included at
`.github/workflows/build-windows.yml`.  Push this folder to a GitHub repo and
either:

- run the workflow manually from the **Actions** tab, or
- push a version tag (`git tag v1.0 && git push --tags`)

The built `HydraulicStudio.exe` is uploaded as a downloadable artifact (or
attached to the GitHub Release for tagged builds).

## What you get

| | |
|---|---|
| **File** | `dist\HydraulicStudio.exe` |
| **Size** | ~180 MB (onefile, bundled) |
| **Window** | Real native window via Microsoft Edge WebView2 |
| **Browser** | None — uses the OS-native webview, NOT a browser tab |
| **Console** | Hidden during normal run, shown only for errors |
| **First run** | May install WebView2 runtime if missing (auto, ~100 MB) |

## Requirements on the build machine

- **Windows 10 (1803+) or Windows 11**, 64-bit
- **Python 3.11+** (3.12 also fine) — <https://www.python.org/downloads/>
- **~2 GB free disk** for the build cache
- **~500 MB free disk** for the final `.exe`
- Internet access for `pip install` (only at build time)

## Requirements on the target machine

- **Windows 10 (1803+) or Windows 11**
- **WebView2 runtime** — pre-installed on Windows 11 and most Windows 10.
  If missing, the app prompts to install it (one-time, ~100 MB).
  Manual install: <https://developer.microsoft.com/microsoft-edge/webview2/>

## File layout

```
canals_ui/
├── launcher.py                       ← entry point (pywebview + Streamlit)
├── launcher_simple.py                ← fallback (browser-based, no pywebview)
├── app.py                            ← Streamlit UI (unchanged)
├── open_channel.py                   ← hydraulic module
├── structures.py                     ← hydraulic module
├── earth_canal.py                    ← hydraulic module
├── requirements.txt                  ← runtime deps
├── hydraulic.spec                    ← PyInstaller spec (native window build)
├── hydraulic_simple.spec             ← PyInstaller spec (browser-based build)
├── build_windows.bat                 ← one-click build (Windows)
└── .github/workflows/build-windows.yml  ← cloud build (GitHub Actions)
```

## Which launcher should I pick?

- **`launcher.py` + `hydraulic.spec`** (default) — opens a **native OS
  window** using Microsoft Edge WebView2. Looks and feels like a real
  desktop app.  No browser is opened.
- **`launcher_simple.py` + `hydraulic_simple.spec`** — opens the app in
  the user's default browser. Smaller `.exe` (~150 MB) and works on
  machines without WebView2.

To use the simple version, run:

```bat
pyinstaller hydraulic_simple.spec --noconfirm --clean
```

instead of `hydraulic.spec`.

## Customising the build

- **Add an icon** — drop an `icon.ico` file in the project root and edit
  `hydraulic.spec` to set `icon="icon.ico"` in the `EXE(...)` block.
- **Smaller exe** — set `upx=True` (already on) and install
  [UPX](https://upx.github.io/) for ~30% size reduction.
- **Console window** — change `console=True` to `console=False` in
  `hydraulic.spec` to hide the console entirely.
- **Custom port** — edit `find_free_port()` in `launcher.py`.

## Troubleshooting

| Problem | Fix |
|---|---|
| `python is not recognized` | Install Python 3.11+ and tick "Add to PATH" during install |
| `ModuleNotFoundError: No module named 'X'` | Re-run the build script; it will reinstall deps |
| `failed to execute script` | Run `HydraulicStudio.exe` from a `cmd` window to see the traceback |
| Blank window on first run | Install WebView2 from <https://developer.microsoft.com/microsoft-edge/webview2/> |
| Antivirus flags the exe | Common for PyInstaller output. Add an exception or sign the binary |

## Running from source (no build)

If you just want to run the app without building:

```bat
pip install -r requirements.txt
streamlit run app.py
```

…and open <http://localhost:8501> in your browser. The `.exe` build is
purely for distribution.
