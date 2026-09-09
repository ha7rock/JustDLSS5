# JustDLSS5 v0.2.5 · 玩家测试版 / Preview

安装核心更新至 DLSS5-Autopilot **v1.7.3**，包含 v1.7.2–v1.7.3 的检测、配置、下载与诊断修复。

- 启动时恢复游戏库，后台复查变化；重新扫描可发现新游戏。继续过滤不存在的游戏程序。
- 手动选择 EXE 后使用所选程序检测。
- 高级设置增加 OptiScaler 分支选择，包括 y4my4my4m 和 wilsjo2 PreSR。
- 增加可选 OpenXR 支持，默认关闭，安装前说明全局层的影响。
- 随包提供 HTTPS 证书，保留 Windows 证书信任与验证。

下载 `JustDLSS5-v0.2.5-windows-x64.zip`，完整解压并运行 `JustDLSS5.exe`。无需安装 Python；不要单独移动 EXE。更新时关闭旧版本，解压到新目录；游戏组件须由用户主动更新。

附 `SHA256SUMS.txt`、`BUILD-INFO.json` 和对应源码材料。第三方许可在应用目录 `LICENSES` 中。

通过离线接口、UI、CLI、缓存、配置、下载回退和 PE 解析回归，以及打包启动和证书检查。本轮没有对真实游戏安装，也未验证 VR / PreSR 的实际效果；两者明确标为实验性、未实测。反作弊检测不是兼容或账号安全保证，请勿用于联网／反作弊游戏。程序未签名，与 NVIDIA 无关。应用更新仍通过下载页面进行。

反馈：[提交问题](https://github.com/ha7rock/JustDLSS5/issues/new?template=bug-report.yml)，请附游戏、版本、平台、配置、复现步骤和截图。

## English

Updates the installation engine to Autopilot **v1.7.3**. Adds cached library startup with changed-game checks, fixes explicit executable selection, exposes OptiScaler builds and opt-in OpenXR, and bundles CA certificates without disabling TLS verification.

Extract the full Windows x64 ZIP into a new folder and run `JustDLSS5.exe`. Close the previous version first. Python, dependency licenses, checksums, build metadata and corresponding source materials are provided. Game components are updated only on request.

Offline regression and packaged startup/certificate checks passed. VR and PreSR remain experimental and untested on real hardware; this update does not claim new game compatibility. Avoid online/anti-cheat games. Unsigned community software, not affiliated with NVIDIA.

Thanks to [DLSS5-Autopilot](https://github.com/Kizzuwatnaa/DLSS5-Autopilot) and its component authors.
