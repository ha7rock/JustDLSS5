# JustDLSS5 v0.2.6 · 玩家测试版 / Preview

安装核心更新至 DLSS5-Autopilot **v1.8.0**。

- 修复 32 位 Vulkan 层被同名 64 位层覆盖；此前的安装需要用户主动重新安装组件才能获得修复。
- 新增“运行分析”：读取日志和 Windows 崩溃记录，根据目标帧率建议渲染区域。仅点击“应用建议”才修改配置，下次启动游戏生效。
- 高级设置可选择光线重建版本；仅适用于已有该组件且安装路线支持的游戏。替换前备份，卸载时还原。
- 设置中可更改游戏内面板快捷键，重新安装组件后生效。
- 安装前显示驱动 / HDR 提示，更多操作可查看上游社区兼容报告。反馈继续提交到 JustDLSS5 Issues。
- 继承下载重试、路径越界防护、Steam 残留目录及诊断修复。DLSS / 帧生成运行时从 NVIDIA 官方仓库获取；神经渲染组件仍依赖上游编排的来源。

下载 `JustDLSS5-v0.2.6-windows-x64.zip`，完整解压到新目录，关闭旧版后运行 `JustDLSS5.exe`。无需安装 Python。附源码材料、第三方许可、`SHA256SUMS.txt` 和 `BUILD-INFO.json`。

本轮验证使用临时文件、模拟日志与离线回归，并检查 Windows 打包启动和证书。没有执行真实游戏安装或 VR / PreSR 测试，不保证具体游戏兼容。性能建议是估算，日志来自不同场景时可能不准。反作弊检测不代表安全许可，请勿用于联网／反作弊游戏。程序未签名，与 NVIDIA 无关。

[反馈问题](https://github.com/ha7rock/JustDLSS5/issues/new?template=bug-report.yml)：请附游戏、版本、平台、显卡驱动、配置、复现步骤和截图。

## English

Updates the engine to Autopilot **v1.8.0**. Fixes the 32-bit Vulkan layer collision and inherits download, path validation and detection fixes. Adds session analysis with Windows crash records, target-FPS suggestions applied only on request, ray reconstruction replacement for eligible games, configurable overlay keys, driver/HDR notes and upstream community reports.

Extract the entire Windows x64 ZIP into a new folder. Close the old application before launching the new one. Existing game components require an explicit reinstall to receive the Vulkan fix. Suggested tuning applies on the next game launch.

Offline regressions and Windows startup/certificate checks are included; no real-game or VR validation is claimed for this update. Estimates depend on comparable game sessions. Avoid online and anti-cheat games. Unsigned community software, not affiliated with NVIDIA.
