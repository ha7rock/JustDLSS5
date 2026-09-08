# JustDLSS5 玩家测试版

这是用于收集兼容性和使用问题的预发布版本。应用可检测游戏、配置和管理画面组件；不是 NVIDIA 官方产品，也不保证所有游戏和显卡组合都能使用。

## 开始使用

1. 下载 Release 中的 `JustDLSS5-v<版本>-windows-x64.zip`，完整解压到可写目录。
2. 运行文件夹内的 `JustDLSS5.exe`。不要只拷贝 EXE，`_internal` 和许可文件需要一并保留。
3. 扫描游戏，或手动添加游戏目录。先确认选中的游戏、EXE 和图形接口正确。
4. 先看“预览变更”，再决定是否安装。关闭游戏后再安装或卸载组件。
5. 遇到问题，从应用的“反馈问题”打开 Issue 表单，补充游戏版本、平台、显卡驱动、配置、复现步骤和截图。

下载与版本说明：https://github.com/ha7rock/JustDLSS5/releases

问题反馈：https://github.com/ha7rock/JustDLSS5/issues/new?template=bug-report.yml

## 测试边界

- 首轮优先测试离线单机游戏。不要将反作弊提示当作完整名单；未标红也不代表游戏允许注入插件。不要用联网或反作弊游戏试探封禁风险。
- 测试前自行备份游戏存档和重要配置。工具的组件备份不能代替完整备份，也不能保证恢复其他模组的状态。
- 先记录原版能否启动，再记录安装后的启动、画面和性能，最后记录卸载后的启动结果。请分别反馈，不把“安装成功”当作“游戏正常”。
- 界面、后台任务和打包启动有自动检查。真实游戏验证以 Release 链接的测试记录为准；没有记录的组合就是未验证。
- 下载依赖 GitHub 及第三方站点。下载失败不一定是游戏兼容性问题；保留任务日志中的错误。
- 当前仅检查新版本并打开发行页面，不会自动覆盖程序或游戏组件。更新时退出旧版，解压新版到新目录。
- 程序尚未做商业代码签名。`SHA256SUMS.txt` 用于核对下载文件是否一致，不代表安全认证；不需要关闭杀毒软件来测试。

界面默认中文，可在左下角切换英文。设置与缓存保存在 `%LOCALAPPDATA%\dlss5-autopilot`，这是为兼容上游保留的目录名。

## English quick start

Extract the complete Windows x64 ZIP and run `JustDLSS5.exe`. Keep `_internal` beside it. Switch the language in the lower-left corner. Scan or add a game folder, verify the executable/API, and preview changes before installing. Start with offline single-player games; an absent anti-cheat warning is not a safety guarantee. Back up saves and configuration first.

Report the game/version/store, Windows and GPU/driver versions, selected components, reproduction steps, screenshots and logs through **Report a problem**. This is a community prerelease, not an NVIDIA product. Game compatibility is unverified unless a published test record says otherwise.
