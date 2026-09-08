# JustDLSS5 v0.2.4 · 玩家测试版 / Public preview

JustDLSS5 把游戏扫描、画面组件安装和配置管理放到一个桌面界面中。支持中文和英文，安装核心来自 DLSS5-Autopilot，当前固定为 **v1.7.1**。

这是首次面向玩家收集反馈的预发布版本，不是稳定版。欢迎反馈扫描识别、窗口布局、配置操作和具体游戏中的问题。

## 下载

- **普通用户：**下载 `JustDLSS5-v0.2.4-windows-x64.zip`，完整解压，运行 `JustDLSS5.exe`。保留同目录的 `_internal`；无需自行安装 Python。
- **核对文件：**`SHA256SUMS.txt`。PowerShell 中可用 `Get-FileHash <下载文件> -Algorithm SHA256` 核对。
- **源码与许可：**应用内含 `LICENSES` 和第三方说明；`JustDLSS5-v0.2.4-source-materials.zip` 包含应用及对应依赖源码。
- **构建记录：**`BUILD-INFO.json` 包含代码提交、工作流编号、依赖版本和文件摘要。

## 能做什么

- 扫描本机游戏，也可以手动添加目录。
- 查看识别结果，选择组件路线和配置，安装前预览变更。
- 管理组件安装、卸载和配置方案。
- 中文／英文界面，支持窗口缩放；后台操作显示进度或加载状态。
- 从应用直接打开问题反馈表单，预填版本与游戏信息。

## 测试范围与注意事项

前端、调用衔接、命令行和打包启动经过自动检查。维护者已反馈进行过真实游戏测试，但尚未整理可核验的逐游戏记录，因此本版本不提供“已兼容游戏名单”，也不宣称所有组合均可用。上游测试不能证明新增前端绝无问题。

首轮请使用离线单机游戏，并先备份存档和重要配置。反作弊检测不完整，未出现警告也不表示允许安装插件；请勿用于联网／反作弊游戏。JustDLSS5 是社区工具，与 NVIDIA 无关。

组件下载依赖第三方站点；下载失败、游戏无法启动和应用界面异常请分别描述。此版本不包含上游 v1.7.2 的新增功能。程序尚未签名，摘要用于核对文件一致性，不是安全认证。应用更新目前提供检查和下载页面入口，不自动覆盖文件。

使用说明：[玩家测试说明](https://github.com/ha7rock/JustDLSS5/blob/main/docs/TESTING-PREVIEW.zh-CN.md)

问题反馈：[提交 Issue](https://github.com/ha7rock/JustDLSS5/issues/new?template=bug-report.yml)。请附游戏与版本、来源平台、Windows、显卡与驱动、所选配置、复现步骤和截图；不涉及游戏的问题可填“不涉及游戏”。

感谢 [DLSS5-Autopilot](https://github.com/Kizzuwatnaa/DLSS5-Autopilot) 及相关组件作者。

## English

First public preview of JustDLSS5, a Chinese/English Windows desktop interface for game detection and graphics component management. The installation engine is pinned to DLSS5-Autopilot **v1.7.1**.

Download the Windows x64 ZIP, extract it completely and run `JustDLSS5.exe`. Python is included. The release also provides SHA-256 checksums, build metadata and corresponding dependency sources.

This is a community testing release, not a stable version or an NVIDIA product. Automated UI/integration and startup checks do not guarantee game compatibility; no verified per-game compatibility list is claimed. Start with offline single-player games, back up saves/configuration, and avoid anti-cheat or online titles. Please report reproducible issues using the in-app feedback entry or GitHub Issues.
