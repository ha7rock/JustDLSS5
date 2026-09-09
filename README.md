<p align="center">
  <img src="docs/images/app-icon.png" alt="JustDLSS5" width="96" height="96">
</p>

<h1 align="center">JustDLSS5</h1>

<p align="center"><strong>DLSS 5, less hassle.</strong></p>

<p align="center">
  A Windows desktop tool for scanning games, installing graphics components,<br>
  and managing DLSS 5–related setup. Qt (PySide) UI with Simplified Chinese and English.
</p>

<p align="center">
  <strong>v0.2.5 · Player preview</strong> · install core: DLSS5-Autopilot <strong>v1.7.3</strong>
</p>

<p align="center">
  <a href="./README.zh-CN.md">中文</a> ·
  <a href="#download">Download</a> ·
  <a href="#features">Features</a> ·
  <a href="#important-notes">Notes</a> ·
  <a href="#credits--license">License</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-0.2.5-blue" alt="version 0.2.5">
  <img src="https://img.shields.io/badge/status-player%20preview-orange" alt="player preview">
  <img src="https://img.shields.io/badge/platform-Windows%20x64-lightgrey" alt="Windows x64">
  <img src="https://img.shields.io/badge/engine-Autopilot%20v1.7.3-informational" alt="Autopilot v1.7.3">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT">
</p>

---

## Download

Download the Windows x64 package from [Releases](https://github.com/ha7rock/JustDLSS5/releases): `JustDLSS5-v0.2.5-windows-x64.zip`.

1. Extract the full archive to a writable folder.
2. Run `JustDLSS5.exe`. Keep `_internal` and the license files next to it; do not copy only the EXE.
3. The portable build does not require a separate Python install.
4. To verify integrity, use `SHA256SUMS.txt`. PowerShell example: `Get-FileHash <file> -Algorithm SHA256`.

The same release also includes `BUILD-INFO.json` (build metadata) and `JustDLSS5-v0.2.5-source-materials.zip` (application and matching dependency sources).

Testing guide: [docs/TESTING-PREVIEW.zh-CN.md](docs/TESTING-PREVIEW.zh-CN.md). Feedback: [open an issue](https://github.com/ha7rock/JustDLSS5/issues/new?template=bug-report.yml), or use **Report a problem** in the app.

> This is a community player preview, not a stable release, and it is not affiliated with NVIDIA.

---

## Screenshots

| Chinese UI | English UI |
| --- | --- |
| ![Library · Chinese](docs/images/library.zh-CN.png) | ![Library · English](docs/images/library.en.png) |

*Screenshots use sample game data for illustration.*

---

## Overview

Configuring DLSS 5–related components by hand often means locating packages, matching graphics APIs, and editing paths — tedious and easy to get wrong. Upstream [DLSS5-Autopilot](https://github.com/Kizzuwatnaa/DLSS5-Autopilot) already implements the install flow. JustDLSS5 builds an independent desktop UI on top of that logic for scanning libraries, choosing routes, previewing changes, and handling uninstall or restore.

| | Manual setup | DLSS5-Autopilot | **JustDLSS5** |
|---|---|---|---|
| UI | None | Upstream tooling | Independent Qt (PySide) desktop app |
| Languages | — | Upstream | Simplified Chinese / English |
| Game library | Manual | Upstream flow | Scan local games, add folders, view install status |
| Install core | Manual | Upstream | Currently Autopilot **v1.7.3** (`core/`) |
| Maintenance | Manual | Upstream | Preview, diagnose, uninstall, restore backups |
| Distribution | — | Upstream | Preview ZIP, checksums, licenses and source materials |

---

## Features

**Install & library**
- Detect the game environment and offer install routes
- Download and configure components; preview changes before applying
- Scan local games or add directories; view install status

**Configuration & maintenance**
- Adjust parameters; save and reload profiles
- Diagnose issues; uninstall; restore from backups

**Per-game options**
- Manual graphics API selection, remembered per game
- FSR frame generation and RTX 40 MFG controls when applicable

**UI & feedback**
- Simplified Chinese / English UI; resizable window
- Background tasks show progress on the related action button
- In-app feedback (pre-fills version and selected game)
- Update check opens the release page and does **not** overwrite the app automatically

**Additional tools**
- Screen / window capture (shared start/stop with the camera)
- Video enhancement and RTX Remix related tools

**Safety**
- Titles with anti-cheat require confirmation before install or batch reinstall (default: cancel)
- Absence of a warning does not mean the game allows plugins

---

## Compared with DLSS5-Autopilot

| | DLSS5-Autopilot | JustDLSS5 |
|---|---|---|
| Role | Upstream install engine / tooling | Desktop UI on that logic |
| Version | Upstream releases | Currently **v1.7.3** (`backend-version.json`) |
| UI | Upstream | Independent Qt app, Chinese and English |
| Package | Upstream project | Portable ZIP, SHA-256, build info, licenses and sources |
| License | Upstream | MIT for JustDLSS5 code; upstream copyright retained |

Install-related code lives in `core/`. See [docs/UPSTREAM-AND-SOURCES.zh-CN.md](docs/UPSTREAM-AND-SOURCES.zh-CN.md) and [docs/UPSTREAM_README.md](docs/UPSTREAM_README.md). This preview does **not** include upstream v1.7.2 features.

---

## Important notes

- Automated checks cover UI, integration, CLI, and packaged startup. There is **no published “verified games” list**; combinations not documented separately should be treated as unverified.
- Prefer **offline single-player** titles for initial testing. Back up saves and important configuration before installing. Component backups from this tool are not a full game backup.
- Anti-cheat detection is incomplete; **no warning does not mean it is safe to install**. Do not use online or anti-cheat titles for exploratory testing.
- Components are downloaded from third-party sites. A download failure is not necessarily a game compatibility issue — keep the task log.
- The binary is not commercially code-signed. SHA-256 only confirms file integrity, not security certification.
- As a preview build, issues may still occur. Please report problems with reproducible steps.

Details: [docs/TESTING-PREVIEW.zh-CN.md](docs/TESTING-PREVIEW.zh-CN.md).

**GPU notes** *(summarized from upstream/community material in `docs/`; not project benchmarks)*
- Upstream tooling provides paths for RTX 50 / 40 / 20–30
- GTX and GPUs older than RTX 20 are not supported
- The ecosystem is still changing; this page makes no FPS claims

---

## Build from source

For development and contribution (Windows x64, Python 3.12):

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-desktop.txt
python autopilot_desktop.py
```

```bat
build-desktop.bat
```

Output: `dist/v0.2.5/JustDLSS5/JustDLSS5.exe`. Keep `_internal` next to the executable.

Maintainer notes: [docs/MAINTAINING.zh-CN.md](docs/MAINTAINING.zh-CN.md).

---

## Credits & license

**Credits**
- Install core: [Kizzuwatnaa/DLSS5-Autopilot](https://github.com/Kizzuwatnaa/DLSS5-Autopilot)
- The project may use components such as ReShade, RenoDX, Feeder, OptiScaler, DXVK, and RTX Remix. See [docs/THIRD-PARTY-NOTICES.md](docs/THIRD-PARTY-NOTICES.md) and [docs/UPSTREAM-AND-SOURCES.zh-CN.md](docs/UPSTREAM-AND-SOURCES.zh-CN.md)

**License**
- JustDLSS5 project code: **MIT**
- Retain upstream copyright for Autopilot-derived parts
- Third-party components, NVIDIA runtimes, and game mods have their own licenses. The source repository does not include those binaries; the portable package ships dependency license notes separately

---

## Docs

- [docs/TESTING-PREVIEW.zh-CN.md](docs/TESTING-PREVIEW.zh-CN.md)
- [docs/RELEASE-v0.2.5.md](docs/RELEASE-v0.2.5.md)
- [docs/THIRD-PARTY-NOTICES.md](docs/THIRD-PARTY-NOTICES.md)
- [docs/MAINTAINING.zh-CN.md](docs/MAINTAINING.zh-CN.md)
- [docs/UPSTREAM-AND-SOURCES.zh-CN.md](docs/UPSTREAM-AND-SOURCES.zh-CN.md) · [docs/UPSTREAM_README.md](docs/UPSTREAM_README.md)

---

<p align="center">JustDLSS5 · v0.2.5 player preview · MIT · community tool, not affiliated with NVIDIA</p>
