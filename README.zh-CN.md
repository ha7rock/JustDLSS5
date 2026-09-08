<p align="center">
  <img src="docs/images/app-icon.png" alt="JustDLSS5" width="96" height="96">
</p>

<h1 align="center">JustDLSS5</h1>

<p align="center"><strong>DLSS 5，少一点折腾。</strong></p>

<p align="center">
  Windows 桌面应用：扫描游戏、安装画面组件、<br>
  管理 DLSS 5 相关配置 — 独立 Qt（PySide）界面，中英双语。
</p>

<p align="center">
  <strong>v0.2.4 · 玩家测试版</strong> · 安装引擎钉死 DLSS5-Autopilot <strong>v1.7.1</strong>
</p>

<p align="center">
  <a href="./README.md">English</a> ·
  <a href="#下载">下载</a> ·
  <a href="#功能">功能</a> ·
  <a href="#测试边界">边界</a> ·
  <a href="#致谢与许可">许可</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-0.2.4-blue" alt="version 0.2.4">
  <img src="https://img.shields.io/badge/status-player%20preview-orange" alt="player preview">
  <img src="https://img.shields.io/badge/platform-Windows%20x64-lightgrey" alt="Windows x64">
  <img src="https://img.shields.io/badge/engine-Autopilot%20v1.7.1-informational" alt="Autopilot v1.7.1">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT">
</p>

---

## 下载

**玩家：**到 [Releases](https://github.com/ha7rock/JustDLSS5/releases) 下载 Windows x64 包（`JustDLSS5-v0.2.4-windows-x64.zip`）。

1. **完整解压**到可写目录。
2. 运行 `JustDLSS5.exe`。保留同目录 `_internal` 与许可文件；不要只拷一个 EXE。
3. 便携包**不需要**自行安装 Python。
4. 可选核对：`SHA256SUMS.txt` — PowerShell：`Get-FileHash <文件> -Algorithm SHA256`。

同版本还提供：`BUILD-INFO.json`（构建记录）、`JustDLSS5-v0.2.4-source-materials.zip`（应用与依赖源码材料）。

玩家说明：[docs/TESTING-PREVIEW.zh-CN.md](docs/TESTING-PREVIEW.zh-CN.md) · 反馈：[提交 Issue](https://github.com/ha7rock/JustDLSS5/issues/new?template=bug-report.yml)（或应用内「反馈问题」）。

> 这是**社区玩家测试版**，不是稳定版，**与 NVIDIA 无隶属关系**。

---

## 截图

| 中文界面 | 英文界面 |
| --- | --- |
| ![游戏库 · 中文](docs/images/library.zh-CN.png) | ![游戏库 · 英文](docs/images/library.en.png) |

*游戏库截图使用示意 mock 数据，非真实库存。*

---

## 为什么是 JustDLSS5

手工配 DLSS 5 相关组件：找包、对 API、改路径，容易踩坑。上游 [DLSS5-Autopilot](https://github.com/Kizzuwatnaa/DLSS5-Autopilot) 已沉淀安装业务逻辑 — JustDLSS5 用独立桌面 UI 包住它，扫库、选路线、预览、维护，少在命令行里耗。

| | 手工配置 | DLSS5-Autopilot | **JustDLSS5** |
|---|---|---|---|
| 界面 | 无 | 上游工具流 | 独立 Qt（PySide）桌面应用 |
| 语言 | — | 上游 | 中英双语 UI |
| 游戏库 | 自己找 | 上游流程 | 扫描本机、手动加目录、看安装状态 |
| 安装引擎 | 自己搞 | 上游 | 钉死 Autopilot **v1.7.1**（`core/`） |
| 维护 | 手工 | 上游 | 预览、诊断、卸载、还原备份 |
| 分发 | — | 上游 | 玩家测试 ZIP + 摘要 + 许可／源码材料 |

---

## 功能

**安装与游戏库**
- 检测游戏环境，给出安装路线
- 下载／配置组件；应用前可预览
- 扫描本机或手动加目录；查看安装状态

**档案与维护**
- 调参；保存／载入档案
- 诊断、卸载、从备份还原

**按游戏控制**
- 手动选择图形 API，并按游戏记住
- 适用时提供 FSR 帧生成、RTX 40 MFG 相关控制

**桌面体验**
- 中英界面；可缩放窗口
- 后台任务在触发按钮上显示进度／加载
- 应用内反馈表单（预填版本与所选游戏）
- 更新检查会打开发行页 — **不会**自动覆盖程序

**扩展**
- 屏幕／窗口捕获（与摄像头共用开始／停止生命周期）
- 视频增强工具 · RTX Remix 工具

**安全**
- 反作弊游戏在安装或批量重装前需**显式确认**（默认取消）
- 警告**不构成**「该游戏一定允许注入」的保证

---

## 与 DLSS5-Autopilot 对比

| | DLSS5-Autopilot | JustDLSS5 |
|---|---|---|
| 角色 | 上游安装引擎／工具 | 在其逻辑之上的桌面产品 UI |
| 引擎 | 上游发版 | 钉死 **v1.7.1**（`backend-version.json`） |
| 界面／语言 | 上游 | 独立 Qt · 中英双语 |
| 玩家包装 | 上游项目 | 便携 ZIP、SHA-256、构建元数据、许可与源码材料 |
| 许可 | 上游 | JustDLSS5 项目代码 MIT；保留上游版权 |

业务逻辑在 `core/`。详见 [docs/UPSTREAM-AND-SOURCES.zh-CN.md](docs/UPSTREAM-AND-SOURCES.zh-CN.md)、[docs/UPSTREAM_README.md](docs/UPSTREAM_README.md)。本预览**不含**上游 v1.7.2 新能力。

---

## 测试边界

- 有界面／衔接／命令行／打包启动的自动检查。**不提供「已兼容游戏名单」** — 没有公开记录的组合＝未验证。
- 首轮优先**离线单机**。先备份存档与重要配置。工具的组件备份不能代替完整备份。
- 反作弊检测不完整；**没警告 ≠ 安全**。不要用联网／反作弊游戏试探封禁风险。
- 组件下载依赖第三方站点。下载失败 ≠ 游戏不兼容 — 请保留任务日志。
- 程序**未做**商业代码签名。摘要只核对文件一致性，不是安全认证。
- 预期有毛刺；请用可复现步骤反馈。

完整说明：[docs/TESTING-PREVIEW.zh-CN.md](docs/TESTING-PREVIEW.zh-CN.md)。

**显卡现实** *（据 `docs/` 中上游／社区说明归纳，非本仓库基准测试）*
- 上游工具链存在 RTX 50／40／20–30 社区路径
- GTX 及低于 RTX 20 **无法运行**
- 非官方早期生态，组件会变；此处不写帧数承诺

---

## 从源码构建

给贡献者（Windows x64、Python 3.12）：

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-desktop.txt
python autopilot_desktop.py
```

```bat
build-desktop.bat
```

产物：`dist/v0.2.4/JustDLSS5/JustDLSS5.exe` — 请保留同目录 `_internal`。

维护说明：[docs/MAINTAINING.zh-CN.md](docs/MAINTAINING.zh-CN.md)。

---

## 致谢与许可

**致谢**
- 安装引擎／业务逻辑：[Kizzuwatnaa/DLSS5-Autopilot](https://github.com/Kizzuwatnaa/DLSS5-Autopilot)
- 项目与上游涉及的生态组件，包括 ReShade、RenoDX、Feeder、OptiScaler、DXVK、RTX Remix 等 — 详见 [docs/THIRD-PARTY-NOTICES.md](docs/THIRD-PARTY-NOTICES.md)、[docs/UPSTREAM-AND-SOURCES.zh-CN.md](docs/UPSTREAM-AND-SOURCES.zh-CN.md)

**许可**
- JustDLSS5 项目代码：**MIT**
- 源自 Autopilot 的逻辑请保留上游版权
- 第三方组件／NVIDIA 运行时／游戏 mod：各自许可 — 源码仓不附带这些二进制；便携发行包另附依赖许可材料

---

## 文档

- [docs/TESTING-PREVIEW.zh-CN.md](docs/TESTING-PREVIEW.zh-CN.md) — 玩家测试说明
- [docs/RELEASE-v0.2.4.md](docs/RELEASE-v0.2.4.md) — v0.2.4 发行说明
- [docs/THIRD-PARTY-NOTICES.md](docs/THIRD-PARTY-NOTICES.md) — 第三方声明
- [docs/MAINTAINING.zh-CN.md](docs/MAINTAINING.zh-CN.md) — 维护说明
- [docs/UPSTREAM-AND-SOURCES.zh-CN.md](docs/UPSTREAM-AND-SOURCES.zh-CN.md) · [docs/UPSTREAM_README.md](docs/UPSTREAM_README.md)

---

<p align="center">JustDLSS5 · v0.2.4 玩家测试版 · MIT · 社区工具，与 NVIDIA 无关</p>
