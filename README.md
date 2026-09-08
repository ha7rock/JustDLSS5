<p align="center">
  <img src="docs/images/app-icon.png" alt="JustDLSS5" width="96" height="96">
</p>

<h1 align="center">JustDLSS5</h1>

<p align="center"><strong>DLSS 5, less hassle.</strong></p>

<p align="center">
  A Windows desktop app to scan games, install graphics components,<br>
  and manage DLSS 5–related setup. Qt (PySide) UI in Chinese and English.
</p>

<p align="center">
  <strong>v0.2.4 · Player preview</strong> · install core from DLSS5-Autopilot <strong>v1.7.1</strong>
</p>

<p align="center">
  <a href="./README.zh-CN.md">中文</a> ·
  <a href="#download">Download</a> ·
  <a href="#what-it-does">Features</a> ·
  <a href="#read-this-first">Limits</a> ·
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

Get the Windows x64 ZIP from [Releases](https://github.com/ha7rock/JustDLSS5/releases): `JustDLSS5-v0.2.4-windows-x64.zip`.

1. Extract the **whole** archive somewhere writable.
2. Run `JustDLSS5.exe`. Keep `_internal` and the license files next to it — don’t copy only the EXE.
3. The portable build does **not** need a separate Python install.
4. Optional check: `SHA256SUMS.txt`. In PowerShell: `Get-FileHash <file> -Algorithm SHA256`.

Same release also has `BUILD-INFO.json` (how this build was made) and `JustDLSS5-v0.2.4-source-materials.zip` (app + matching dependency sources).

How to test: [docs/TESTING-PREVIEW.zh-CN.md](docs/TESTING-PREVIEW.zh-CN.md). Problems: [open an issue](https://github.com/ha7rock/JustDLSS5/issues/new?template=bug-report.yml), or use **Report a problem** in the app.

> Community player preview — not a stable release, and **not affiliated with NVIDIA**.

---

## Screenshots

| Chinese UI | English UI |
| --- | --- |
| ![Library · Chinese](docs/images/library.zh-CN.png) | ![Library · English](docs/images/library.en.png) |

*Library shots use mock games for illustration.*

---

## Why this exists

Setting up DLSS 5–related components by hand usually means chasing downloads, matching APIs, and hoping you didn’t break a path. [DLSS5-Autopilot](https://github.com/Kizzuwatnaa/DLSS5-Autopilot) already handles the install flow; JustDLSS5 puts an independent desktop UI on top so you can scan, pick a route, preview changes, and clean up without living in a terminal.

| | Hand setup | DLSS5-Autopilot | **JustDLSS5** |
|---|---|---|---|
| UI | None | Upstream tooling | Independent Qt (PySide) desktop app |
| Languages | — | Upstream | Chinese + English |
| Game library | Manual | Upstream flow | Scan local games, add folders, see install status |
| Install core | You | Upstream | Currently Autopilot **v1.7.1** (`core/`) |
| Maintenance | Manual | Upstream | Preview, diagnose, uninstall, restore backups |
| Downloads | — | Upstream | Player-preview ZIP, checksums, licenses + sources |

---

## What it does

**Install & library**
- Detect the game setup and suggest install routes
- Download and configure components; preview before applying
- Scan local games or add a folder; see what’s already installed

**Config & maintenance**
- Tweak settings; save and reload profiles
- Diagnose problems; uninstall; restore from backups

**Per game**
- Manual graphics API choice, remembered per game
- FSR frame gen and RTX 40 MFG controls when they apply

**Day to day**
- Chinese / English UI; resizable window
- Background work shows progress on the button you clicked
- In-app feedback (fills in version and selected game)
- Update check opens the release page — it **won’t** overwrite the app for you

**Also**
- Screen / window capture (shared start/stop with the camera)
- Video tools and RTX Remix helpers

**Safety**
- Anti-cheat titles ask for **explicit confirm** before install or batch reinstall (default: cancel)
- No warning does **not** mean the game allows plugins

---

## vs DLSS5-Autopilot

| | DLSS5-Autopilot | JustDLSS5 |
|---|---|---|
| Role | Upstream install engine / tooling | Desktop UI on that logic |
| Version | Upstream releases | Currently **v1.7.1** (`backend-version.json`) |
| UI | Upstream | Own Qt app, Chinese + English |
| Player package | Upstream project | Portable ZIP, SHA-256, build info, licenses + sources |
| License | Upstream | MIT for JustDLSS5 code; keep upstream copyright |

Install logic lives in `core/`. See [docs/UPSTREAM-AND-SOURCES.zh-CN.md](docs/UPSTREAM-AND-SOURCES.zh-CN.md) and [docs/UPSTREAM_README.md](docs/UPSTREAM_README.md). This preview does **not** include upstream v1.7.2 features.

---

## Read this first

- There are automated checks for UI, wiring, CLI, and packaged startup. **No “supported games” list** — if it isn’t written down, treat it as untested.
- First round: prefer **offline single-player**. Back up saves and important configs yourself. The tool’s component backup is not a full game backup.
- Anti-cheat detection is incomplete; **no warning ≠ safe**. Don’t use online / anti-cheat titles to “see if you get banned.”
- Components download from third-party sites. A failed download isn’t the same as “game incompatible” — keep the task log.
- The binary isn’t commercially code-signed. Checksums only show the file isn’t corrupted.
- It’s a preview. Small issues happen — please report with steps you can reproduce.

More detail: [docs/TESTING-PREVIEW.zh-CN.md](docs/TESTING-PREVIEW.zh-CN.md).

**GPUs** *(from upstream/community notes in `docs/`, not our benchmarks)*
- Upstream tooling has paths for RTX 50 / 40 / 20–30
- GTX and anything older than RTX 20 won’t run
- Unofficial, moving ecosystem — no FPS promises here

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

Output: `dist/v0.2.4/JustDLSS5/JustDLSS5.exe` — keep `_internal` beside it.

Maintainer notes: [docs/MAINTAINING.zh-CN.md](docs/MAINTAINING.zh-CN.md).

---

## Credits & license

**Credits**
- Install core: [Kizzuwatnaa/DLSS5-Autopilot](https://github.com/Kizzuwatnaa/DLSS5-Autopilot)
- Ecosystem pieces the project may use, including ReShade, RenoDX, Feeder, OptiScaler, DXVK, RTX Remix, and others — see [docs/THIRD-PARTY-NOTICES.md](docs/THIRD-PARTY-NOTICES.md) and [docs/UPSTREAM-AND-SOURCES.zh-CN.md](docs/UPSTREAM-AND-SOURCES.zh-CN.md)

**License**
- JustDLSS5 project code: **MIT**
- Keep upstream copyright for Autopilot-derived parts
- Third-party components / NVIDIA runtimes / game mods have their own licenses. The source repo doesn’t ship those binaries; the portable release includes dependency license notes separately

---

## Docs

- [docs/TESTING-PREVIEW.zh-CN.md](docs/TESTING-PREVIEW.zh-CN.md) — player preview guide
- [docs/RELEASE-v0.2.4.md](docs/RELEASE-v0.2.4.md) — v0.2.4 notes
- [docs/THIRD-PARTY-NOTICES.md](docs/THIRD-PARTY-NOTICES.md)
- [docs/MAINTAINING.zh-CN.md](docs/MAINTAINING.zh-CN.md)
- [docs/UPSTREAM-AND-SOURCES.zh-CN.md](docs/UPSTREAM-AND-SOURCES.zh-CN.md) · [docs/UPSTREAM_README.md](docs/UPSTREAM_README.md)

---

<p align="center">JustDLSS5 · v0.2.4 player preview · MIT · community tool, not affiliated with NVIDIA</p>
