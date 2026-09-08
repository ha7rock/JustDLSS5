<p align="center">
  <img src="docs/images/app-icon.png" alt="JustDLSS5" width="96" height="96">
</p>

<h1 align="center">JustDLSS5</h1>

<p align="center"><strong>DLSS 5, less hassle.</strong></p>

<p align="center">
  Windows desktop tool to detect games, download graphics components,<br>
  and install &amp; manage DLSS 5 setup — with a Qt (PySide) UI in Chinese and English.
</p>

<p align="center">
  <a href="./README.zh-CN.md">中文</a> ·
  <a href="#quick-start">Quick start</a> ·
  <a href="#features">Features</a> ·
  <a href="#credits--license">License</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-0.2.0-blue" alt="version 0.2.0">
  <img src="https://img.shields.io/badge/platform-Windows%20x64-lightgrey" alt="Windows x64">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB" alt="Python 3.12">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT">
  <img src="https://img.shields.io/badge/status-private%20pre--release-orange" alt="private pre-release">
</p>

---

## Screenshot

![JustDLSS5 game library (Chinese UI)](docs/images/library.zh-CN.png)

*Game library view (Chinese UI). Screenshot uses mock game data for illustration.*

---

## Why JustDLSS5

Setting up DLSS 5–related components by hand means hunting downloads, matching APIs, and hoping you didn't break a game path. Upstream [DLSS5-Autopilot](https://github.com/Kizzuwatnaa/DLSS5-Autopilot) already encodes the install business logic — JustDLSS5 wraps that logic in an independent desktop UI so you can scan, choose routes, preview, and maintain without living in the terminal.

| | Hand setup | DLSS5-Autopilot | **JustDLSS5** |
|---|---|---|---|
| UI | None | Upstream tooling | Independent Qt (PySide) desktop app |
| Languages | — | Upstream | Chinese + English UI |
| Game library | Manual | Upstream flow | Scan local games, manual dirs, install status |
| Install engine | You | Upstream | Pinned to Autopilot **v1.7.1** (`core/`) |
| Maintenance | Manual | Upstream | Preview, diagnose, uninstall, restore backups |

JustDLSS5 is a **community tool**. It is **not affiliated with NVIDIA**. Support depends on the game, GPU, and third-party components you install.

---

## Features

**Component install**
- Detect the game environment and offer install routes
- Download and configure graphics components

**Game library**
- Scan locally installed games
- Add directories manually
- See install status at a glance

**Config profiles**
- Adjust parameters per need
- Save and reload profiles

**Maintenance**
- Preview changes before applying
- Diagnose issues
- Uninstall components
- Restore from backups

**Per-game controls**
- Manual graphics API selection, remembered per game
- FSR frame generation and RTX 40 MFG controls when applicable

**Extras**
- Screen / window capture (shared start/stop lifecycle with camera)
- Video enhancement tools
- RTX Remix tools

**Safety**
- Anti-cheat titles require **explicit confirm** before install or batch reinstall (default: cancel)

---

## Comparison vs DLSS5-Autopilot

| | DLSS5-Autopilot | JustDLSS5 |
|---|---|---|
| Role | Upstream install engine / tooling | Desktop product UI on top of that logic |
| Engine version | Upstream releases | Pinned to **v1.7.1** (`backend-version.json`) |
| UI | Upstream | Independent Qt (PySide) |
| i18n | Upstream | Chinese + English UI |
| Distribution | Upstream project | Private pre-release; build from source (no public GitHub Releases yet) |
| License | Upstream | MIT for JustDLSS5 project code; retain upstream copyright |

Business logic lives in `core/`, based on [Kizzuwatnaa/DLSS5-Autopilot](https://github.com/Kizzuwatnaa/DLSS5-Autopilot). See [docs/UPSTREAM-AND-SOURCES.zh-CN.md](docs/UPSTREAM-AND-SOURCES.zh-CN.md) and [docs/UPSTREAM_README.md](docs/UPSTREAM_README.md).

---

## Quick start

> **Honest status:** the repo is currently **private**. There are **no public GitHub Releases** yet — this is a private pre-release. Build from source on Windows.

### Requirements

- Windows x64
- Python 3.12
- A supported NVIDIA GPU path (see [Requirements & limits](#requirements--limits))

### Run from source

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-desktop.txt
python autopilot_desktop.py
```

### Build the desktop app

```bat
build-desktop.bat
```

Output:

```text
dist/v0.2.0/JustDLSS5/JustDLSS5.exe
```

Keep the `_internal` folder next to the exe — the app needs it.

---

## Requirements & limits

**Platform**
- Windows x64 only (as built today)
- Python 3.12 for source runs

**GPU reality** *(summarized from upstream/community docs preserved in `docs/`)*
- RTX 50 / 40 / 20–30 community paths exist in upstream tooling
- GTX and GPUs below RTX 20 do **not** run
- This is an unofficial, early ecosystem — components change

Do **not** treat any path as guaranteed FPS or compatibility. JustDLSS5 does not publish benchmarks.

**Anti-cheat**
- Games with anti-cheat need explicit confirmation before install / batch reinstall
- Confirmations and warnings are **not guarantees** that a title will accept the install

**Not NVIDIA**
- Not affiliated with NVIDIA
- The repo does **not** ship NVIDIA runtimes or game mod assets
- Third-party components, NVIDIA runtimes, and game mods have their **own** licenses

**Support**
- Results depend on game + GPU + third-party components
- Community tool — expect rough edges while the ecosystem moves

---

## Credits & license

**Credits**
- Install engine / business logic: [Kizzuwatnaa/DLSS5-Autopilot](https://github.com/Kizzuwatnaa/DLSS5-Autopilot)
- Ecosystem tools & components referenced by the project and upstream, including ReShade, RenoDX, Feeder, OptiScaler, DXVK, RTX Remix, and others

**License**
- JustDLSS5 project code: **MIT**
- Retain upstream copyright for Autopilot-derived logic
- Third-party components / NVIDIA runtimes / game mods: their own licenses — this repo does not redistribute those binaries

---

## Docs

- [docs/UPSTREAM-AND-SOURCES.zh-CN.md](docs/UPSTREAM-AND-SOURCES.zh-CN.md) — upstream & sources
- [docs/UPSTREAM_README.md](docs/UPSTREAM_README.md) — upstream README (preserved)
- Maintenance / contributor notes: see `docs/MAINTAINING.zh-CN.md` (recommended home for backend update, tests, and source map — previously the Chinese README)

---

<p align="center">JustDLSS5 · v0.2.0 · MIT · community tool, not affiliated with NVIDIA</p>