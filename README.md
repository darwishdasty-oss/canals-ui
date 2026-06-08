# Hydraulic Engineering Design Studio

A unified Streamlit web UI that wraps the three Python hydraulic-design modules you provided.

**UI:** minimalist dark theme — charcoal background with a single lime accent, hairline borders, no gradients, no clutter.  Rendered as a **floating native window** with full macOS-style chrome (title bar, menu bar, toolbar, sidebar, status bar).

## Two ways to run

### A. From source (any OS)

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open <http://localhost:8501>.

### B. As a native Windows .exe

See [BUILD.md](BUILD.md). One command on a Windows 10/11 machine:

```bat
build_windows.bat
```

…produces a single `dist\HydraulicStudio.exe` that opens in its own native window (no browser).

## What you get

| Page | Module | What it does |
|------|--------|--------------|
| Home | — | Module index, project panel, console |
| 01 · Open Channel | `open_channel.py` | Trapezoidal/rectangular/triangular/circular/parabolic sections · Manning · Chezy · Bernoulli · critical/normal depth · specific-energy curve · GVF profile · optimal hydraulic section |
| 02 · Structures | `structures.py` | Sluice & radial gates · siphons (with cavitation check) · pressure breakers (stilling well / impact basin / cascade) |
| 03 · Earth Canals | `earth_canal.py` | Lacey silt theory · Kennedy theory (CVR) · side-by-side comparison |
| About | — | Module map, run instructions |

## Project layout

```
canals_ui/
  ├── app.py             # Streamlit UI (the wrapper)
  ├── launcher.py        # Native-window launcher (for .exe build)
  ├── open_channel.py    # ← your 1.py, renamed
  ├── structures.py      # ← your 2.py, renamed (truncated tail closed cleanly)
  ├── earth_canal.py     # ← your 3.py, renamed
  ├── requirements.txt
  ├── hydraulic.spec     # PyInstaller spec (for the .exe build)
  ├── build_windows.bat  # One-click .exe builder
  ├── BUILD.md           # Detailed build instructions
  └── README.md
```

## Notes

- The three original files were renamed to valid Python module names so they can be imported cleanly.
- `2.py` was truncated in the source ZIP. The tail was closed cleanly so the file imports; `HydraulicStructuresSystem.comprehensive_design()` was completed with a minimal stub that calls the three sub-designers.
- All original classes, methods, and equations are unchanged. The UI is a thin wrapper.
- The native-window look uses pure CSS — no extra runtime dependencies.

## Stack

Streamlit · NumPy · SciPy · Matplotlib · pywebview (for .exe) · PyInstaller (for .exe)
