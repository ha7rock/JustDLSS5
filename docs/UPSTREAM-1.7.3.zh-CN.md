# v1.7.3 检查与接入

日期：2026-09-09。新正式 Release 发布于 2026-09-08 22:37:52 UTC。
固定候选：f26717ad3369e93f9de3972734132402ec8a4444。
升级前基线：v1.7.1 / 8225ffff7f6fc6530ba2f204e34e3689f59d5b0c。
上一份评估：v1.7.2 / 577f986f20cf3dc87caeca0ccf331d9dea3528c3，本次一并接入。

## 代码与行为

比较了候选相对运行基线、相对已评估版本的代码差异。重点文件为 core/library.py、feedcfg.py、diagnose.py、pe.py、video.py、optiscaler.py、installer.py、profiles.py 和旧 Tk 界面。

- 配置数值读取兼容逗号小数，避免插件写出的配置导致安装中断。
- FFmpeg 查询改为 BtbN 的 releases/tags/latest，增加文件名匹配和固定下载地址回退。
- pe_imports(path, delay=False) 新增延迟导入解析；降低单独 d3d9 导入证据的优先级。
- 诊断区分未完成安装、DXVK 与 ReShade 接入、多次启动日志和不同模块错误；不能将诊断规则当作所有游戏的兼容保证。
- sources.cached_json 与 optiscaler.archive_name 让预览从所选分支的缓存选择归档，不发网络请求。
- 增加 dlssg_sm86.ini 冲突组件线索；实际清理、备份和卸载仍需在接入时复核。

## 前端接入要求

1. 游戏库缓存不会随替换核心自动生效。library.save/load/forget 由上游 core/gui.py 显式调用，我们的 BackendService.scan 仍直接调用 games.scan_all。需要接入后台加载、主动扫描、保存和操作后的缓存刷新。
2. 缓存包含上游游戏对象和 Tk 行数据，不能直接当作 Qt 模型。需重新处理安装状态、图标和反作弊信息，并保留我们的残留目录过滤。缓存按 schema、核心版本、GPU 和文件状态失效；前端检测规则变化也应能使其失效。
3. 特别回归 EXE 删除但文件夹保留、离线磁盘、权限受限、缓存损坏、中文路径和主动发现新游戏，避免重新出现残留游戏。
4. optiscaler.BUILDS 新增 wilsjo2 PreSR 分支，默认仍为原 DLSS-NR 分支。上游标为未实测；不要默认选择或宣传已验证。profiles.FIELDS 新增 opti_build，控件、旧方案与保存需一起适配。
5. v1.7.2 待办仍适用：games.enrich(..., chosen=True)、Options.opti_build/vr、certifi 及冻结包资源、根 CLI 参数、OpenXR 默认关闭及卸载边界。详见上一份评估。
6. 4K 与滚动修复属于旧 Tk 界面，不移植其控件代码；保留我们的 Qt 布局与操作反馈规范。

## 依赖与写入边界

新增可选来源 wilsjo2/OptiScaler-DLSSNR-PreSR-Multipass，实际接入时核对下载内容与许可，不预装进应用包。FFmpeg 仍来自 GitHub 的 ZIP，变化在查询和回退；OptiScaler 保持 ZIP/7z 支持。

新缓存为 %LOCALAPPDATA%/dlss5-autopilot/library.json，采用临时文件与替换保存。本增量未新增类似 OpenXR 的全局层，但从 v1.7.1 升级仍包含 v1.7.2 的 HKCU OpenXR 层与证书处理变化。

## 验证

固定提交执行 tools/update_backend.py f26717ad3369e93f9de3972734132402ec8a4444 dry-run 成功：66 个属性与调用签名、42 项 UI 测试、2 项 CLI、7 项产品测试、6 组 INI 检查。

新增八项离线检查全部通过：逗号小数配置；缓存版本/GPU失效；EXE变更重查；删除目录过滤；手动API覆盖缓存；指定分支离线预览；FFmpeg API失败后的固定地址回退；最后一段ReShade日志选择。网络均 mock，文件仅写临时测试目录。

本地检查材料：build/upstream-173-targeted.py、build/upstream-173-check/、build/upstream-173-from-172.json、build/upstream-173-from-171.json（均被忽略，不进入发行包）。

已完成本产品回归及 EXE 打包启动、证书检查；新增 PE32/PE32+ 延迟导入用例。未运行上游完整测试套件，也未运行真实性能、游戏、VR 或捕获测试。

## 结论

JustDLSS5 0.2.5 已接入固定 v1.7.3 核心和上游 CLI。前端支持游戏库缓存、chosen=True、OptiScaler 分支与可选 OpenXR；保留残留目录过滤和反作弊提示。PreSR 与 VR 明确标注未实测。

接入检查：69 项接口属性与调用签名；44 项 UI、3 项 CLI、7 项产品、3 项发行包、13 项上游适配测试及 6 组 INI 检查。固定 certifi 2026.7.22，发行材料加入 MPL 许可与对应源码。核心文件保持与上游一致，更新工具今后同步 CLI 并运行适配测试。每日任务继续完成适配、版本与构建，不以评估报告代替交付。未安装游戏组件，未改变仓库可见性。

来源：https://github.com/Kizzuwatnaa/DLSS5-Autopilot/releases/tag/v1.7.3
差异：https://github.com/Kizzuwatnaa/DLSS5-Autopilot/compare/577f986f20cf3dc87caeca0ccf331d9dea3528c3...f26717ad3369e93f9de3972734132402ec8a4444
