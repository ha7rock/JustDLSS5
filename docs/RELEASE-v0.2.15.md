# JustDLSS5 v0.2.15 · 玩家测试版 / Player preview

引擎更新至 Autopilot v2.0.5，固定提交 `cc9a94187fabe2754ec913cc8eca481b56f2082a`。

- 修正下载选择：OptiScaler 排除同一仓库中的其他工具包；Feeder 默认渠道排除名称带测试标记的发行版。组件检查解释此前误装测试版、错误变体或代理 DLL 缺失的情况。
- 继承模拟器与旧版 Unreal 游戏识别、实验性 DirectX 8 接入、链接目录安装、子进程 DLL 搜索环境及运行诊断修复。
- 在“检查安装与运行”中可补充“未能启动”或“自行退出”，让排查建议对应实际情况。OptiScaler 退出阶段的异常单独记录，不直接算作运行失败。
- 新增 wilsjo2 PreSR + RTX 40 多帧生成选项，默认不选；已知非 RTX 40 显卡禁用。需要游戏原生 DLSS 补帧，不能与 FSR 补帧同时发挥作用。

下载 Windows x64 ZIP，完整解压后运行 `JustDLSS5.exe`。发行附源码材料、第三方许可、`SHA256SUMS.txt` 和 `BUILD-INFO.json`。游戏组件仍在用户请求安装时下载。

保持玩家测试版渠道。离线回归和 Windows 构建检查不等于真实游戏或头显兼容性验证；DX8、新增 RTX 40 多帧生成组合、VR 和自动试装均无本次实机验证。正在单独开发的游戏库 PR 不包含在此次维护发布中。与 NVIDIA 无关。

## English

Updates the installation core to Autopilot v2.0.5 at the fixed commit above, retaining the Qt interface.

OptiScaler resolution now rejects unrelated archives, and Feeder's default channel excludes test builds by tag. Component checks distinguish wrong variants, unintended beta installs and missing proxy DLLs. Includes upstream emulator/legacy Unreal detection, experimental DX8, linked-folder installation, child-process DLL environment and diagnostic fixes.

Session checks accept reports that a game never started or closed itself. OptiScaler teardown faults are explained separately. Adds the optional PreSR + RTX 40 MFG build, disabled on known unsupported GPUs; it needs native DLSS frame generation.

Extract the complete Windows x64 ZIP. Matching source materials, third-party licenses, checksums and build metadata accompany this player preview. Offline and build checks do not verify real-game or headset compatibility. The pending library redesign is separate. Not affiliated with NVIDIA.
