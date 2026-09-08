# Third-party software and corresponding source

JustDLSS5 project code is MIT licensed. The original DLSS5-Autopilot copyright and MIT license are retained in `LICENSE.txt`. The MIT license does not relicense the dependencies below.

## Included runtime

- Qt 6.11.2: Qt Core, Gui, Widgets, Network, OpenGL and Svg, with the Windows, GIF, ICO, JPEG and SVG plugins used by this application. Distributed under the available LGPL v3 option, with third-party components retaining their own licenses.
- PySide6 Essentials and Shiboken6 6.11.2: Python bindings, distributed under the available LGPL v3 option. The PyPI wheels support both open-source and commercial licensing; their commercial-license file does not replace the open-source terms we use.
- CPython 3.12.10 (GitHub release builds) or 3.12.14 (local development builds) and standard-library dependencies: Python Software Foundation terms and the respective component licenses, including OpenSSL, libffi, bzip2, xz/liblzma, zlib and Expat.
- PyInstaller 6.22.2 bootloader and runtime hooks: see its included `COPYING.txt`, including the bootloader distribution exception and runtime-file terms.
- Microsoft Visual C++ runtime libraries: Microsoft runtime terms. These files are not covered by the project's MIT license.

`LICENSES/` contains license texts, copyright notices, and Qt attribution records from the pinned official source archives, along with package and Python distribution license files. It is intentionally broader than the modules included in the executable; inclusion of a notice does not mean that every source component is shipped as a binary.

## Source and rebuilding

The same GitHub Release supplies `JustDLSS5-v<version>-source-materials.zip` alongside the Windows ZIP, without a separate charge. It includes the JustDLSS5 source at the build commit and unmodified Qt base, Qt SVG, PySide/Shiboken, Python and Python dependency source archives. `DEPENDENCY-SOURCES.json` lists exact upstream locations, versions, commits where available and SHA-256 values. `BUILD-INFO.json` identifies the application commit, runtime versions, workflow run and bundled file hashes. Keep the source-materials asset available for as long as the binary is offered.

Release page: https://github.com/ha7rock/JustDLSS5/releases

Qt and PySide are dynamically loaded from `_internal`. We impose no restriction on replacing these libraries with compatible modified versions, or on reverse engineering needed to debug modifications to LGPL-covered libraries. Keep ABI-compatible versions and architectures together. For a rebuild, unpack the JustDLSS5 source, install Python 3.12.10 x64, install `requirements-desktop.txt`, and run `python tools/build_desktop.py`. To use modified Qt/PySide, build matching bindings and install them into that build environment first. Dependency sources include their own build instructions. No activation key is required.

License references:

- https://doc.qt.io/qt-6/licensing.html
- https://doc.qt.io/qt-6/licenses-used-in-qt.html
- https://doc.qt.io/qtforpython-6/licenses.html
- https://pypi.org/project/PySide6-Essentials/6.11.2/
- https://pyinstaller.org/en/stable/license.html
- https://visualstudio.microsoft.com/license-terms/vs2022-cruntime/

## Downloaded game components

The application ZIP does not include game files, NVIDIA models, ReShade, OptiScaler, Feeder, RenoDX add-ons, Remix mods or video tools. Features can download third-party components when selected. Those downloads retain their own terms and are not licensed by this application's MIT license. JustDLSS5 is an independent community project and is not affiliated with NVIDIA.
