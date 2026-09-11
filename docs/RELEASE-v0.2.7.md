# JustDLSS5 v0.2.7 · 玩家测试版 / Preview

安装核心更新至 DLSS5-Autopilot **v1.8.1**。

- 修复部分 Vulkan 游戏和嵌套目录中的 DLSS 识别；完整游戏 EXE 优先于同目录的试用版；扫描和缓存按 EXE 去重。
- 损坏的下载缓存会重新获取；MFG 来源变化时跳过该可选组件并提示，避免中断其余安装。
- Bridge 配置增加保留标记，避免被新运行时覆盖。已有 Bridge 安装需主动重新安装组件才能获得修复。
- OptiScaler 安装会启用日志、保留用户日志级别，并关闭指向不含神经渲染功能的主线更新提示。
- 新驱动下的 Standalone 建议仅对支持该路线的游戏显示；OptiScaler 明确提示需在游戏设置中开启 FSR / XeSS。
- 继承诊断修正；保留 JustDLSS5 的界面、滚轮防误触和现有反馈入口。

下载 `JustDLSS5-v0.2.7-windows-x64.zip`，完整解压到新目录，关闭旧版后运行 `JustDLSS5.exe`。无需安装 Python。附程序、对应源码、第三方许可、`SHA256SUMS.txt` 和 `BUILD-INFO.json`。

本轮验证为离线回归、临时文件夹具和 Windows 打包启动 / 证书检查，没有执行真实游戏安装或 VR 测试。Standalone 仍为实验性路线，不保证兼容。请勿用于联网／反作弊游戏。程序未签名，与 NVIDIA 无关。

[反馈问题](https://github.com/ha7rock/JustDLSS5/issues/new?template=bug-report.yml)：请附游戏、版本、平台、显卡驱动、配置、复现步骤和截图。

## English

Updates the engine to Autopilot **v1.8.1**: Vulkan and nested DLSS detection, full-game executable preference, executable-based library deduplication, invalid cache replacement, optional MFG failures, persistent Bridge configuration and OptiScaler logging/update notices.

The desktop now explains FSR/XeSS prerequisites and suggests Standalone only when available for the selected game. Existing Bridge installs need an explicit component reinstall for the configuration fix.

Extract the complete Windows x64 ZIP into a new folder and run `JustDLSS5.exe`. Python, licenses, corresponding sources, checksums and build information are included. Offline and packaged startup checks do not guarantee real-game compatibility. Standalone remains experimental. Avoid online/anti-cheat games. Unsigned community software, not affiliated with NVIDIA.
