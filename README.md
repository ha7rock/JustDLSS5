<p align="center">
  <img src="docs/images/app-icon.png" alt="JustDLSS5" width="96" height="96">
</p>

<h1 align="center">JustDLSS5</h1>

<p align="center"><strong>DLSS 5, less hassle.</strong></p>

<p align="center">
  Windows desktop app to scan games, install graphics components,<br>
  and manage DLSS 5–related setup — Qt (PySide) UI in Chinese and English.
</p>

<p align="center">
  <strong>v0.2.4 · Player preview</strong> · engine pinned to DLSS5-Autopilot <strong>v1.7.1</strong>
</p>

<p align="center">
  <a href="./README.zh-CN.md">中文</a> ·
  <a href="#download">Download</a> ·
  <a href="#features">Features</a> ·
  <a href="#preview-limits">Limits</a> ·
  <a href="#credits--license">License</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-0.2.4-blue" alt="version 0.2.4">
  <img src="https://img.shields.io/badge/status-player%20preview-orange" alt="player preview">
  <img src="https://img.shields.io/badge/platform-Windows%20x64-lightgrey" alt="Windows x64">
  <img src="https://img.shields.io/badge/engine-Autopilot%20v1.7.1-informational" alt="Autopilot v1.7.1">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT">
</p>

---

## Download

**Players:** get the Windows x64 ZIP from [Releases](https://github.com/ha7rock/JustDLSS5/releases) (`JustDLSS5-v0.2.4-windows-x64.zip`).

1. Extract the **entire** archive to a writable folder.
2. Run `JustDLSS5.exe`. Keep `_internal` and the bundled license files beside it.
3. No separate Python install needed for the portable build.
4. Optional: verify with `SHA256SUMS.txt` — in PowerShell: `Get-FileHash <file> -Algorithm SHA256`.

Also on the release: `BUILD-INFO.json` (build record) and `JustDLSS5-v0.2.4-source-materials.zip` (app + dependency sources).

Player guide: [docs/TESTING-PREVIEW.zh-CN.md](docs/TESTING-PREVIEW.zh-CN.md) · Feedback: [open a bug report](https://github.com/ha7rock/JustDLSS5/issues/new?template=bug-report.yml) (or use **Report a problem** in the app).

> This is a **community player preview**, not a stable release and **not affiliated with NVIDIA**.

---

## Screenshots

| Chinese UI | English UI |
| --- | --- |
| ![Library · Chinese](docs/images/library.zh-CN.png) | ![Library · English](docs/images/library.en.png) |

*Library views use mock game data for illustration.*

---

## Why JustDLSS5

Hand-wiring DLSS 5–related components means chasing downloads, matching APIs, and hoping you did not break a game path. Upstream [DLSS5-Autopilot](https://github.com/Kizzuwatnaa/DLSS5-Autopilot) already owns the install logic — JustDLSS5 wraps it in an independent desktop UI so you can scan, pick routes, preview, and maintain without living in the terminal.

| | Hand setup | DLSS5-Autopilot | **JustDLSS5** |
|---|---|---|---|
| UI | None | Upstream tooling | Independent Qt (PySide) desktop app |
| Languages | — | Upstream | Chinese + English UI |
| Game library | Manual | Upstream flow | Scan local games, add dirs, install status |
| Install engine | You | Upstream | Pinned to Autopilot **v1.7.1** (`core/`) |
| Maintenance | Manual | Upstream | Preview, diagnose, uninstall, restore backups |
| Distribution | — | Upstream | Player-preview ZIP + checksums + license materials |

---

## Features

**Install & library**
- Detect game environment and offer install routes
- Download / configure components; preview before apply
- Scan local games or add folders; see install status

**Profiles & maintenance**
- Tune parameters; save / reload profiles
- Diagnose issues; uninstall; restore backups

**Per-game controls**
- Manual graphics API choice, remembered per game
- FSR frame generation and RTX 40 MFG controls when applicable

**Desktop polish**
- Chinese / English UI; resizable window
- Background tasks show progress / loading on the action that started them
- In-app feedback form (pre-fills version and selected game)
- Update check opens the release page — **does not** auto-overwrite the app

**Extras**
- Screen / window capture (shared start/stop lifecycle with camera)
- Video enhancement tools · RTX Remix tools

**Safety**
- Anti-cheat titles need **explicit confirm** before install or batch reinstall (default: cancel)
- Warnings are **not** a guarantee that a title allows injection

---

## Comparison vs DLSS5-Autopilot

| | DLSS5-Autopilot | JustDLSS5 |
|---|---|---|
| Role | Upstream install engine / tooling | Desktop product UI on that logic |
| Engine | Upstream releases | Pinned to **v1.7.1** (`backend-version.json`) |
| UI / i18n | Upstream | Independent Qt · Chinese + English |
| Player packaging | Upstream project | Portable ZIP, SHA-256, build metadata, license + source materials |
| License | Upstream | MIT for JustDLSS5 project code; retain upstream copyright |

Business logic lives in `core/`. See [docs/UPSTREAM-AND-SOURCES.zh-CN.md](docs/UPSTREAM-AND-SOURCES.zh-CN.md) and [docs/UPSTREAM_README.md](docs/UPSTREAM_README.md). Upstream **v1.7.2** is not included in this preview.

---

## Preview limits

- Automated UI / integration / CLI / packaged-startup checks exist. **No verified per-game compatibility list** is published — unlisted combinations are unverified.
- First round: prefer **offline single-player** games. Back up saves and important configs first. Tool backups are not a full game backup.
- Anti-cheat detection is incomplete; **no warning ≠ safe**. Do not use online / anti-cheat titles to “test bans.”
- Component downloads depend on third-party sites. Download failures are not the same as game incompatibility — keep task logs.
- Binary is **not** commercially code-signed. Checksums verify integrity, not trust.
- Expect rough edges; please report reproducible issues.

Full notes: [docs/TESTING-PREVIEW.zh-CN.md](docs/TESTING-PREVIEW.zh-CN.md).

**GPU reality** *(from upstream/community docs in `docs/`, not a JustDLSS5 benchmark)*
- RTX 50 / 40 / 20–30 community paths exist in upstream tooling
- GTX and GPUs below RTX 20 do **not** run
- Unofficial, early ecosystem — components change; no FPS claims here

---

## Build from source

For contributors (Windows x64, Python 3.12):

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-desktop.txt
python autopilot_desktop.py
```

```bat
build-desktop.bat
```

Output: `dist/v0.2.4/JustDLSS5/JustDLSS5.exe` — keep `_internal` next to the exe.

Maintainer notes: [docs/MAINTAINING.zh-CN.md](docs/MAINTAINING.zh-CN.md).

---

## Credits & license

**Credits**
- Install engine / business logic: [Kizzuwatnaa/DLSS5-Autopilot](https://github.com/Kizzuwatnaa/DLSS5-Autopilot)
- Ecosystem components referenced by the project and upstream, including ReShade, RenoDX, Feeder, OptiScaler, DXVK, RTX Remix, and others — see [docs/THIRD-PARTY-NOTICES.md](docs/THIRD-PARTY-NOTICES.md) and [docs/UPSTREAM-AND-SOURCES.zh-CN.md](docs/UPSTREAM-AND-SOURCES.zh-CN.md)

**License**
- JustDLSS5 project code: **MIT**
- Retain upstream copyright for Autopilot-derived logic
- Third-party components / NVIDIA runtimes / game mods: their own licenses — this repo does not ship those binaries in source; the portable release documents bundled dependency licenses separately

---

## Docs

- [docs/TESTING-PREVIEW.zh-CN.md](docs/TESTING-PREVIEW.zh-CN.md) — player preview guide
- [docs/RELEASE-v0.2.4.md](docs/RELEASE-v0.2.4.md) — v0.2.4 release notes
- [docs/THIRD-PARTY-NOTICES.md](docs/THIRD-PARTY-NOTICES.md) — third-party notices
- [docs/MAINTAINING.zh-CN.md](docs/MAINTAINING.zh-CN.md) — maintainer notes
- [docs/UPSTREAM-AND-SOURCES.zh-CN.md](docs/UPSTREAM-AND-SOURCES.zh-CN.md) · [docs/UPSTREAM_README.md](docs/UPSTREAM_README.md)

---

<p align="center">JustDLSS5 · v0.2.4 player preview · MIT · community tool, not affiliated with NVIDIA</p>
