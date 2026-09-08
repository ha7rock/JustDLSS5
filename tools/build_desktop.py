"""Build with explicit binary provenance; never vendor unrelated host tool DLLs."""
from pathlib import Path
import os
import sys
import PyInstaller.__main__
from PyInstaller.utils.win32.versioninfo import (VSVersionInfo, FixedFileInfo,
    StringFileInfo, StringTable, StringStruct, VarFileInfo, VarStruct)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from frontend.about import NAME, VERSION, REPOSITORY

spec_dir = ROOT / "build" / "desktop-spec"
spec_dir.mkdir(parents=True, exist_ok=True)
version_numbers = tuple(int(part) for part in VERSION.split(".")) + (0,)
version_resource = VSVersionInfo(
    ffi=FixedFileInfo(filevers=version_numbers, prodvers=version_numbers,
                     mask=0x3f, flags=0, OS=0x40004, fileType=1, subtype=0, date=(0, 0)),
    kids=[StringFileInfo([StringTable("040904B0", [
        StringStruct("CompanyName", "JustDLSS5 contributors"),
        StringStruct("FileDescription", NAME + " - Game graphics component manager"),
        StringStruct("FileVersion", VERSION),
        StringStruct("InternalName", NAME),
        StringStruct("OriginalFilename", NAME + ".exe"),
        StringStruct("ProductName", NAME),
        StringStruct("ProductVersion", VERSION),
        StringStruct("Comments", REPOSITORY),
    ])]), VarFileInfo([VarStruct("Translation", [1033, 1200])])])
(spec_dir / "version.txt").write_text(str(version_resource), encoding="utf8")
spec = spec_dir / "desktop.spec"
spec.write_text('''
from pathlib import Path
import os, sys
ROOT = Path(''' + repr(str(ROOT)) + ''')
a = Analysis([str(ROOT / "autopilot_desktop.py")], pathex=[str(ROOT)],
    binaries=[], datas=[(str(ROOT / "docs/MAINTAINING.zh-CN.md"), "docs"), (str(ROOT / "frontend/chevron.svg"), "frontend"), (str(ROOT / "frontend/check.svg"), "frontend"), (str(ROOT / "frontend/justdlss5.ico"), "frontend")],
    hiddenimports=[], hookspath=[], runtime_hooks=[],
    excludes=["tkinter", "core.gui", "core.compareui", "core.remixui"], noarchive=False)
# Some development runtimes augment DLL search even after PATH is sanitized.
# Only ship binaries belonging to Python, our venv, the project, or Windows.
# In particular, Poppler's ICU exports *_78 while Qt needs Windows' ICU API.
allowed = [Path(sys.prefix).resolve(), Path(sys.base_prefix).resolve(),
           ROOT.resolve(), Path(os.environ["SystemRoot"]).resolve()]
# The bundled Python runtime supplies its OpenSSL DLLs outside base_prefix.
# These are explicit imports of _ssl.pyd / _hashlib.pyd, not Qt ICU shims.
python_ssl = {"libssl-3-x64.dll", "libcrypto-3-x64.dll"}
kept = []
for item in a.binaries:
    source = Path(item[1]).resolve()
    # This application uses Qt Widgets only. Do not bundle unused QML,
    # PDF or virtual-keyboard plugins and their additional dependencies.
    name = source.name.lower()
    if "pyside6" in str(source).lower():
        if "plugins" in source.parts:
            plugins = {"qwindows.dll", "qgif.dll", "qico.dll", "qjpeg.dll", "qsvg.dll", "qsvgicon.dll"}
            if name not in plugins:
                continue
        if name.startswith("qt6") and name not in {"qt6core.dll", "qt6gui.dll", "qt6widgets.dll", "qt6svg.dll", "qt6network.dll", "qt6opengl.dll"}:
            continue
        if name == "opengl32sw.dll":
            continue
    if source.name.lower() in python_ssl or any(source.is_relative_to(base) for base in allowed):
        kept.append(item)
    else:
        print("Excluded unrelated host binary:", source.name)
a.binaries = kept
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True,
    name="JustDLSS5", debug=False, bootloader_ignore_signals=False,
    strip=False, upx=False, console=bool(os.environ.get("STUDIO_BUILD_CONSOLE")),
    version=str(ROOT / "build/desktop-spec/version.txt"), icon=str(ROOT / "frontend/justdlss5.ico"))
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False,
               name="JustDLSS5")
''', encoding="utf8")
PyInstaller.__main__.run(["--clean", "--noconfirm", "--distpath", os.environ.get("STUDIO_DIST_DIR", str(ROOT / "dist" / ("v" + VERSION))),
                         "--workpath", str(ROOT / "build" / "qt-packaging"), str(spec)])
