# Universal‑PyInstaller‑Builder

**Universal‑PyInstaller‑Builder** is a lightweight, modern **Windows GUI** for packaging Python projects into standalone executables with **PyInstaller**. It provides a clean, guided workflow—pick your entry script, choose one‑file or one‑dir, add data files, list hidden imports, pick an icon, choose an output folder, and build.

> **Platform:** Windows only (developed and tested on Windows).  
> **Scope:** 100% GUI usage. No terminal commands required.

---

## Features

- **Modern dark UI** (CustomTkinter) with a clear layout.
- **Inline help**: a small “❓” button explains each section directly in the interface.
- **One‑file / one‑dir** builds via a single checkbox.
- **Data bundling**  
  - Add individual files or entire folders.  
  - When prompted, select the destination inside your packaged app (e.g., `.` or `assets/`).
- **Hidden imports**: enter a comma‑separated list for modules PyInstaller might not detect automatically.
- **Icon embedding**: select a `.ico` file for your executable (you can also type a path).
- **Custom output folder**: defaults to `dist`, editable in the UI.
- **Live build log**: real‑time output streaming plus a **Copy log** button for easy sharing.
- **Smart PyInstaller selection** (to reduce “wrong‑environment” builds):  
  1. Prefer a `.venv` next to your **target entry script**.  
  2. If this app is frozen, prefer a `.venv` next to this app.  
  3. Otherwise use the current interpreter.  
  4. Fall back to `pyinstaller` on `PATH`.
- **Optional UPX**: if UPX is installed and on `PATH`, the build uses it automatically.
- **Pre/Post cleanup**: removes the previous `build/` directory and any `*.spec` files in the project root before and after each build to keep outputs clean.

---

## How to Use (GUI)

1. Launch **Universal‑PyInstaller‑Builder** on Windows.  
2. **Entry Point**: choose your main `.py` file.  
3. (Optional) **Executable Name**: set a custom name.  
4. **Additional Data**:  
   - **Add File** or **Add Folder**.  
   - When prompted, choose the destination path inside your bundle (e.g., `.` or `assets/`).  
5. **Hidden Imports**: enter modules as a comma‑separated list (e.g., `package_a.submodule, mypkg.utils`).  
6. **Icon**: select a `.ico` file (or type a path).  
7. **Output Directory**: keep `dist` or select another folder.  
8. **Build Mode**: toggle **Build one‑file executable** as needed.  
9. Click **Build Executable** and monitor the **Build Log**.  
10. Use **Copy log** to copy the full output for troubleshooting or sharing.

---

## How It Works (Under the Hood)

- **PyInstaller invocation**  
  The app decides how to call PyInstaller in this order:  
  1) Python from a `.venv` next to your **target entry script** → `python -m PyInstaller`  
  2) If the app is frozen, Python from a `.venv` next to this app → `python -m PyInstaller`  
  3) The **current interpreter** → `python -m PyInstaller`  
  4) Fallback → `pyinstaller` on `PATH`

- **Command assembly**  
  Based on your selections, the generated build includes:  
  - `--onefile` **or** `--onedir`  
  - `--noconsole` (optimized for GUI applications)  
  - `--exclude-module sitecustomize` and a few stdlib excludes (`unittest`, `test`, `pydoc`)  
  - `--name`, `--icon`, `--add-data`, `--hidden-import`, `--distpath` as configured in the UI  
  - `--upx-dir` if UPX is found on `PATH`

- **Windows environment help**  
  When possible, the app sets `TCL_LIBRARY`/`TK_LIBRARY` for the invoked Python to reduce Tk/Tcl packaging issues on Windows.

- **Artifact hygiene**  
  Before and after each build, the app clears `build/` and any `*.spec` files in the project root to avoid confusion from stale outputs.

---

## Comparison with Other PyInstaller GUIs

### Advantages
- **Simplicity first**: opinionated defaults and a minimal set of controls cover the most common packaging scenarios.
- **Smarter environment picking**: prioritizes a `.venv` alongside your *target* project to reduce mismatched‑environment builds.
- **Clean builds by default**: automatic pre/post cleanup reduces “it worked yesterday” surprises.
- **Focused UX**: consistent dark theme, inline help, readable sections, and a copyable log.

### Downsides
- **Fewer exposed flags** than power‑user GUIs:  
  - No explicit toggle for console apps (the build applies `--noconsole`).  
  - No built‑in debug/verbosity toggles.  
  - No spec‑file viewing/editing UI (and default cleanup removes `*.spec`).  
  - No dedicated UI for advanced collection settings (hooks, binaries, etc.).
- **No cancel button**: once a build starts, it runs to completion; closing mid‑build can leave a background process.
- **Windows‑only** focus: designed and tested on Windows; other platforms are not supported or claimed.

---

## Limitations
 
- **Requires PyInstaller** and a working Python environment on Windows.  
- **Console builds**: not exposed in the UI (the app adds `--noconsole`).  
- **Spec files**: the app deletes any `*.spec` files in the project root before **and** after building.  
- **Cancellation**: no in‑GUI cancellation; if a build hangs, you must terminate the PyInstaller process externally.  
- **UPX**: used only if present on `PATH`; not bundled.  
- **Hidden imports** must be provided by you if auto‑detection misses something.

---

## Troubleshooting

- **“PyInstaller not found”** → ensure PyInstaller is installed in the same environment the app ends up using (ideally a `.venv` next to your entry script).  
- **Tk/Tcl issues in packaged apps** → confirm a consistent Python base; the app attempts to supply `TCL_LIBRARY`/`TK_LIBRARY` when it can infer them.  
- **Missing modules at runtime** → add them to **Hidden Imports** (comma‑separated).  
- **Data files not found** → verify each entry follows `source_path;destination_inside_bundle` and that the destination is correct relative to your app.

---

## Project Structure

- universal_executable_builder.py: Main GUI and build logic  
- utility.py: Tooltips, cleanup helpers, CTkToolTip monkey patches

---

Note: The executable in the repository was created using this application (the application created its own executable).
