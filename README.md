# JustDLSS5

<img src="docs/images/app-icon.png" width="96" height="96" alt="JustDLSS5 图标">

**DLSS 5，少一点折腾。**

JustDLSS5 是一款 Windows 桌面工具，用于检测游戏、下载画面组件，以及管理 DLSS 5 的安装与配置。选择游戏后，查看可用方案，在同一个界面里完成安装、调整和卸载。

![JustDLSS5 游戏库](docs/images/library.zh-CN.png)

*界面示例，使用模拟游戏数据。*

## 功能

- **组件安装**：检测游戏环境，提供安装方案，下载并配置所需组件。
- **游戏管理**：扫描本地游戏，也可手动添加目录，查看各游戏的安装状态。
- **配置方案**：调整参数、保存方案，在需要时重新载入。
- **维护与恢复**：安装前预览变更，出现问题时查看诊断，支持卸载组件与恢复备份。

支持手动选择图形 API，并在适用的游戏和硬件上提供补帧选项。另提供视频增强、屏幕／窗口捕获和 RTX Remix 工具。界面支持简体中文与英文。

## 使用

当前为私有预发布版本（JustDLSS5 0.2.0 / 安装引擎 1.7.1）。从源码构建后运行 `JustDLSS5.exe`，请保留同目录的 `_internal` 文件夹。

1. 扫描游戏库，或添加游戏目录。
2. 选择游戏，查看检测结果和安装设置。
3. 按需预览变更，然后安装。

这是社区工具，与 NVIDIA 无隶属关系。支持情况取决于游戏、显卡和第三方组件；反作弊提示不能覆盖所有游戏。请勿将未标记理解为允许安装插件。具体下载来源与文件位置见 [上游与资源说明](docs/UPSTREAM-AND-SOURCES.zh-CN.md)。

## 开发与构建

Windows x64、Python 3.12：

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements-desktop.txt
.venv/Scripts/python.exe autopilot_desktop.py
```

运行 `build-desktop.bat` 检查接口、执行测试、打包并验证启动。输出为 `dist/v0.2.0/JustDLSS5/JustDLSS5.exe`。

本地构建后可双击 `start-desktop.bat`，始终打开这一版本。

源码结构和后端更新方法见 [维护说明](README.zh-CN.md)。

## 致谢与许可

感谢 **[Kizzuwatnaa / DLSS5-Autopilot](https://github.com/Kizzuwatnaa/DLSS5-Autopilot)** 提供游戏检测、组件编排、安装、备份和卸载的基础。JustDLSS5 延续这些业务能力，独立维护桌面界面与中文体验。原项目介绍保存在 [上游 README](docs/UPSTREAM_README.md)。

也感谢 ReShade、RenoDX、Feeder、OptiScaler、DXVK、RTX Remix 及其他组件作者。各组件的归属和下载地址见 [资源说明](docs/UPSTREAM-AND-SOURCES.zh-CN.md)。

项目代码采用 [MIT 许可证](LICENSE)，保留上游版权。第三方运行库、插件和游戏资源各自适用其许可，不因本项目开源而成为 MIT 授权内容。本仓库不包含 NVIDIA 运行库或游戏模组资源。
