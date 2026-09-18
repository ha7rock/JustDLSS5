# JustDLSS5 v0.2.14 · 玩家测试版 / Player preview

安装引擎更新至 Autopilot v2.0.1，固定提交 `39e5e2b323482b9639b31d0b5589aa6febed6eb4`。保留 JustDLSS5 的 Qt 界面。

- 继承 32 位辅助程序、Vulkan、DXVK、OptiScaler 包选择与诊断修复。
- 游戏“更多”中可更新或还原原生 DLSS 文件（SR / FG / RR），也可还原本工具安装的 Remix 模组。处理前显示确认，操作结果可见。
- 设置中可检查和移除本工具的 OpenXR 注册；可选游戏退出后检查运行记录，默认关闭，不自动启动或试装游戏。
- 自动尝试接入社区排序依据；组件版本检查提示版本相同但需要更换安装包的情况。

Windows x64 ZIP 解压后运行 `JustDLSS5.exe`，保留同目录所有文件。发行附对应源码、依赖许可、`SHA256SUMS.txt` 与 `BUILD-INFO.json`。不包含游戏组件 DLL；安装时按上游来源下载。

这是玩家测试版。离线回归与打包检查不等于真实游戏兼容验证；自动尝试和 VR 为实验性。启用 OpenXR 层会影响当前用户所有 OpenXR 应用。反作弊游戏可能拒绝第三方插件，请遵循游戏规则；本工具不提供保护绕过。未合并的游戏库设计不包含在此维护版本中。与 NVIDIA 无关。

## English

Updates the pinned installation core to Autopilot v2.0.1 while retaining the Qt interface. Includes upstream helper, Vulkan, DXVK, package selection and diagnostic fixes.

The game’s More menu now provides native DLSS runtime update/restore (SR / FG / RR) and restoration of recorded Remix mod installs. Settings provides OpenXR registration management and optional post-session checks (off by default). Automatic trials use community ordering evidence; component checks explain same-version package corrections.

Extract the Windows x64 ZIP and run `JustDLSS5.exe` with all bundled files intact. Matching source materials, dependency licenses, checksums and build metadata are included. Game component DLLs are downloaded from upstream-defined sources when requested.

Player preview: offline regression and build checks do not establish real-game compatibility. Automatic trials and VR remain experimental. OpenXR registration affects all OpenXR apps for the current user. Respect game anti-cheat rules; this tool does not bypass protection. Pending library redesign work is not included. Not affiliated with NVIDIA.
