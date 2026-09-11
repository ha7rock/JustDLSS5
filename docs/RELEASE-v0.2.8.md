# JustDLSS5 v0.2.8 · 玩家测试版 / Preview

检查结果现在按用途展示，不再把结论、提示和排查细节堆在同一段文本中。

- **检查安装与运行 / 运行分析**：共用结果页，先展示结论与需要关注的问题，通过项默认折叠。
- **中文诊断**：翻译当前引擎的固定诊断标题与结论，并适配动态模板；游戏名、路径、版本和错误码保留。部分关键问题附操作建议，完整上游说明可展开，未适配的提示明确保留原文。
- **崩溃和调整建议**：区分近期与较早的 Windows 崩溃记录；渲染比例建议仍需点击应用，下次启动游戏生效。
- **组件版本**：按组件、已安装、最新可用三列展示；检查不会自动替换文件。
- **原始记录**：独立查看并完整复制，复制后显示反馈。

安装核心保持 DLSS5-Autopilot **v1.8.1**，没有改动下载、打补丁或卸载逻辑。外部社区内容和底层技术日志不做自动翻译。

下载 `JustDLSS5-v0.2.8-windows-x64.zip`，完整解压到新目录，关闭旧版后运行 `JustDLSS5.exe`。无需安装 Python。附第三方许可、对应源码材料、`SHA256SUMS.txt` 和 `BUILD-INFO.json`。

本轮验证覆盖离线回归、中文/英文诊断展示、长路径窄窗口、原文复制与 Windows 打包启动；没有执行真实游戏安装或 VR 测试。请勿用于联网／反作弊游戏。程序未签名，与 NVIDIA 无关。

[反馈问题](https://github.com/ha7rock/JustDLSS5/issues/new?template=bug-report.yml)：请附游戏、应用版本、平台、复现步骤和截图。

## English

Installation checks and session analysis now share a structured report: conclusion first, warnings visible, passing checks collapsed. Diagnostic titles and conclusions are localized in the frontend while preserving paths, versions and error codes. Complete upstream details remain available; unrecognized messages are explicitly shown in their original language.

Windows crash records distinguish recent and earlier events. Render scale suggestions still require explicit application. Component versions now use an installed/latest table. Original reports have their own view and copy feedback.

The installation engine remains Autopilot **v1.8.1**. Community content and low-level logs are not automatically translated. Extract the full Windows x64 ZIP into a new directory and run `JustDLSS5.exe`. Offline/UI and packaged startup checks do not guarantee real-game compatibility. Avoid online/anti-cheat games. Unsigned community software, not affiliated with NVIDIA.
