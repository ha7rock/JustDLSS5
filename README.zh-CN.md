<p align="center">
  <img src="docs/images/app-icon.png" alt="JustDLSS5" width="96" height="96">
</p>

<h1 align="center">JustDLSS5</h1>

<p align="center"><strong>DLSS 5，少一点折腾。</strong></p>

<p align="center">
  Windows 桌面工具：检测游戏、下载图形组件、<br>
  安装与管理 DLSS 5 相关配置 — 独立 Qt（PySide）界面，中英双语。
</p>

<p align="center">
  <a href="./README.md">English</a> ·
  <a href="#快速开始">快速开始</a> ·
  <a href="#功能">功能</a> ·
  <a href="#致谢与许可">许可</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-0.2.4-blue" alt="version 0.2.4">
  <img src="https://img.shields.io/badge/platform-Windows%20x64-lightgrey" alt="Windows x64">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB" alt="Python 3.12">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT">
  <img src="https://img.shields.io/badge/status-public%20preview-orange" alt="public preview">
</p>

---

## 截图

![JustDLSS5 游戏库（中文界面）](docs/images/library.zh-CN.png)

*游戏库界面（中文）。截图中的游戏数据为示意 mock，非真实库存。*

---

## 为什么是 JustDLSS5

手工配 DLSS 5 相关组件：找包、对 API、改路径，容易踩坑。上游 [DLSS5-Autopilot](https://github.com/Kizzuwatnaa/DLSS5-Autopilot) 已经沉淀了安装业务逻辑 — JustDLSS5 用独立桌面 UI 包住这套逻辑，让你扫库、选路线、预览变更、做维护，少在命令行里耗。

| | 手工配置 | DLSS5-Autopilot | **JustDLSS5** |
|---|---|---|---|
| 界面 | 无 | 上游工具流 | 独立 Qt（PySide）桌面应用 |
| 语言 | — | 上游 | 中英双语 UI |
| 游戏库 | 自己找 | 上游流程 | 扫描本机、手动加目录、看安装状态 |
| 安装引擎 | 自己搞 | 上游 | 钉死 Autopilot **v1.7.1**（`core/`） |
| 维护 | 手工 | 上游 | 预览、诊断、卸载、还原备份 |

JustDLSS5 是**社区工具**，**与 NVIDIA 无任何隶属关系**。能否跑通取决于游戏、显卡与你安装的第三方组件。

---

## 功能

**组件安装**
- 检测游戏环境，给出安装路线
- 下载并配置图形组件

**游戏库**
- 扫描本机已装游戏
- 手动添加目录
- 一眼看安装状态

**配置档案**
- 按需调参
- 保存 / 重新加载档案

**维护**
- 应用前预览变更
- 诊断问题
- 卸载组件
- 从备份还原

**按游戏控制**
- 手动选择图形 API，并按游戏记住
- 适用时提供 FSR 帧生成、RTX 40 MFG 相关控制

**扩展**
- 屏幕 / 窗口捕获：与摄像头共用开始／停止生命周期
- 视频增强工具
- RTX Remix 工具

**安全**
- 反作弊游戏在安装或批量重装前需**显式确认**（默认取消）

---

## 与 DLSS5-Autopilot 对比

| | DLSS5-Autopilot | JustDLSS5 |
|---|---|---|
| 角色 | 上游安装引擎 / 工具 | 在其逻辑之上的桌面产品 UI |
| 引擎版本 | 上游发版 | 钉死 **v1.7.1**（`backend-version.json`） |
| 界面 | 上游 | 独立 Qt（PySide） |
| 国际化 | 上游 | 中英双语 UI |
| 分发 | 上游项目 | 公开测试版；[下载 Windows x64 版](https://github.com/ha7rock/JustDLSS5/releases/tag/v0.2.4) |
| 许可 | 上游 | JustDLSS5 项目代码 MIT；保留上游版权 |

业务逻辑在 `core/`，基于 [Kizzuwatnaa/DLSS5-Autopilot](https://github.com/Kizzuwatnaa/DLSS5-Autopilot)。详见 [docs/UPSTREAM-AND-SOURCES.zh-CN.md](docs/UPSTREAM-AND-SOURCES.zh-CN.md)、[docs/UPSTREAM_README.md](docs/UPSTREAM_README.md)。

---

## 快速开始

> **玩家测试版：**[下载 Windows x64 版 v0.2.4](https://github.com/ha7rock/JustDLSS5/releases/tag/v0.2.4)。完整解压 ZIP 后运行 `JustDLSS5.exe`，无需自行安装 Python。测试范围与已知限制见发行说明。

### 环境要求

- Windows x64
- Python 3.12
- 受支持的 NVIDIA 显卡路径（见 [要求与限制](#要求与限制)）

### 从源码运行

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-desktop.txt
python autopilot_desktop.py
```

### 构建桌面应用

```bat
build-desktop.bat
```

产物：

```text
dist/v0.2.4/JustDLSS5/JustDLSS5.exe
```

请保留 exe 同目录下的 `_internal` 文件夹，否则无法正常运行。

---

## 要求与限制

**平台**
- 目前仅 Windows x64
- 源码运行需 Python 3.12

**显卡现实** *（据 `docs/` 中保留的上游 / 社区说明归纳，非本仓库实测承诺）*
- 上游工具链存在 RTX 50 / 40 / 20–30 社区路径
- GTX 及低于 RTX 20 的显卡**无法运行**
- 非官方早期生态，组件会变

不要把任何路径当成帧数或兼容性保证。JustDLSS5 **不发布**基准测试数据。

**反作弊**
- 带反作弊的游戏，安装 / 批量重装前需显式确认
- 确认与警告**不构成**「该游戏一定接受安装」的保证

**与 NVIDIA 无关**
- 与 NVIDIA 无隶属、无背书
- 仓库**不附带** NVIDIA 运行时或游戏 mod 资源
- 第三方组件、NVIDIA 运行时、游戏 mod 各有许可

**支持边界**
- 结果取决于游戏 + 显卡 + 第三方组件
- 社区工具，生态变动时请预期毛刺

---

## 致谢与许可

**致谢**
- 安装引擎 / 业务逻辑：[Kizzuwatnaa/DLSS5-Autopilot](https://github.com/Kizzuwatnaa/DLSS5-Autopilot)
- 项目与上游涉及的生态工具与组件，包括 ReShade、RenoDX、Feeder、OptiScaler、DXVK、RTX Remix 等

**许可**
- JustDLSS5 项目代码：**MIT**
- 源自 Autopilot 的逻辑请保留上游版权
- 第三方组件 / NVIDIA 运行时 / 游戏 mod：各自许可 — 本仓库不重新分发这些二进制

---

## 文档

- [docs/UPSTREAM-AND-SOURCES.zh-CN.md](docs/UPSTREAM-AND-SOURCES.zh-CN.md) — 上游与来源
- [docs/UPSTREAM_README.md](docs/UPSTREAM_README.md) — 上游 README（归档保留）
- 维护 / 贡献者说明：见 `docs/MAINTAINING.zh-CN.md`（建议把原中文 README 中的后端更新、测试、源码地图迁到此处）

> **说明：** 本页为产品说明。若你仍看到旧版「维护文档」式 `README.zh-CN.md`，请将其内容迁至 `docs/MAINTAINING.zh-CN.md`，再以本产品页替换仓库根目录的中文 README。

---

<p align="center">JustDLSS5 · v0.2.4 · MIT · 社区工具，与 NVIDIA 无关</p>