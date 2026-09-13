# JustDLSS5 v0.2.9 · 玩家测试版 / Preview

核心更新到 DLSS5-Autopilot **v1.8.2**，固定提交 `c61369318411dedd10a5a536d5a00bd06b223e36`。

- **扫描游戏**：首次扫描完整检测；之后普通扫描只检查新增游戏。按钮旁的下拉菜单可执行完整扫描（含模拟器），扫描期间显示进度反馈并禁用重复操作。
- **Xbox / Game Pass**：Windows 限制读取程序时，可在高级设置中选择 32/64 位并确认图形接口；未完成识别前禁止安装。
- **驱动推荐**：在新驱动且游戏没有原生 DLSS 时，按核心判断推荐 Standalone。页面解释推荐原因，已有安装保留原路线。
- **安装与还原**：继承重复安装时保留原文件备份记录的修复，以及磁盘空间不足提示、MFG 避让其他插件加载器等改进。
- **诊断**：补齐新增中文标题与结论；有效的 Windows 崩溃记录不再与“未运行”结论同时出现。
- **下载**：组件查询在 GitHub API 不可用时回退至发行页面；必要时下载并校验固定版本的 7z 解压助手。应用本身的更新检查仍使用独立入口。

下载 `JustDLSS5-v0.2.9-windows-x64.zip`，完整解压到新目录，关闭旧版后运行 `JustDLSS5.exe`。无需安装 Python。附第三方许可、对应源码、摘要和构建信息。

验证覆盖 103 项离线回归、6 组 INI 检查、前端接口及 Windows 打包启动；未执行真实游戏或 VR 测试。此更新不会自动安装游戏组件。请勿用于联网／反作弊游戏。程序未签名，与 NVIDIA 无关。

[反馈问题](https://github.com/ha7rock/JustDLSS5/issues/new?template=bug-report.yml)

## English

The engine is pinned to Autopilot **v1.8.2**. Regular rescans inspect new games; a separate full scan includes emulators. Protected Xbox executables have explicit architecture/API controls. Driver-aware recommendations explain Standalone and preserve existing install choices.

Inherits original-file backup retention on reinstall, clearer disk-full errors, component release-page fallback and a hash-checked 7z extraction helper. New diagnostic conclusions are localized, and matching Windows crash evidence takes precedence over an empty-session verdict. Product update checks remain separate from the engine updater.

Extract the full Windows x64 ZIP into a new directory. Includes licenses, corresponding source, SHA256SUMS.txt and BUILD-INFO.json. Offline/UI and packaged startup checks do not guarantee real-game compatibility. No game components are installed automatically. Avoid online/anti-cheat games. Unsigned community software, not affiliated with NVIDIA.
