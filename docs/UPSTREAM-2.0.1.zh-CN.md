# 上游 v2.0.1 接入记录

## 触发和边界

2026-09-18T08:46:15.165Z，automation_id=justdlss5 自动触发。此次维护独立于游戏库交互讨论；只在独立工作树 codex/upstream-2.0.1-release 中进行。
基线：主分支 4ea72ef，产品 0.2.13，引擎 v1.9.0（c3bab6da10fbb70cefb03f70464ca876a07316b0）。
检查的最新正式版：v2.0.1，固定提交 39e5e2b323482b9639b31d0b5589aa6febed6eb4。
发布页：https://github.com/Kizzuwatnaa/DLSS5-Autopilot/releases/tag/v2.0.1

## 差异与接入

- 核心与 CLI 按固定提交完整接入；上游 UI 拆分至 core/ui。Qt 界面仍独立维护，不引入 Tk 界面或替换游戏库 PR #5。
- 继承 32 位辅助进程、Vulkan 层重复名称、DXVK 的实际 API 检测、驱动适配、安装诊断及扫描修复。
- OptiScaler PreSR 标准包与 RTX 40 MFG 包区分。同版本但旧包错误时，组件检查也显示重新安装提示，避免只比较版本号。
- autopilot.plan 新增 data/game 参数：传入社区记录，并将 plan_reasons 的依据加入确认界面。第一条仍是用户选定路线，其余按社区证据排序；反作弊与 VR 拒绝规则保留。
- 社区报告显示本游戏该路线的实际样本数量，不将少量自报当作兼容保证。
- 新增原生 DLSS 文件更新和还原入口（游戏“更多”菜单）。scan/newest 在后台执行；update/restore 分别调用上游实现。备份独立于 DLSS 5 安装器；更新默认拒绝反作弊，不暴露绕过选项；断网不妨碍调用还原。逐次确认目录，处理时不能重入或关闭。
- RTX Remix 可还原本工具模组记录，先执行上游 preflight（运行中/写权限检查）。这与卸载 DLSS 5 组件分开。
- 设置中新增 OpenXR 注册检查和移除。明确提示作用于当前用户所有 OpenXR 应用，移除只调用上游的当前用户自有注册清理，不清理其他工具注册。VR 仍需原有安装确认。
- 可选游戏退出后检查：默认关闭，仅窗口运行时采集已安装游戏的进程/模块记录，退出后后台诊断。结果在设置中查看；不会自动启动、试装或卸载。主窗口关闭会停止观察，不增加托盘驻留。
- 新增三项诊断文本翻译。其余动态上游错误保留原文，避免丢失依据。

## 来源、依赖与安全

下载、备份和还原业务保留在 core 中；新 DLSS 更新从上游 NVIDIA 构建目录解析，仍使用现有网络与证书模块。没有新增 Python 依赖。Qt 包仍排除 Tk；Qt/PySide/Python/certifi 等许可和对应源码随原有发布流程校验打包。
维护执行本身未安装、卸载或启动真实游戏，未修改 OpenXR 注册。真实显卡、头显和游戏稳定性不属于离线验证所得结论。

## 验证与发布

已完成接入、验证和玩家测试版发布。接口检查 128 项、原有 107 项回归、新增 9 项维护测试及 INI 检查通过。


### 本次执行结果（2026-09-18 自动触发）

- 固定上游提交完整接入；更新脚本已纳入新增测试，再次 dry-run 通过。
- 本地 Windows 程序启动通过；新增中文管理界面离屏排版检查通过。
- 最终候选提交：fd1f02b6e3254c8458accb9bcc26b9ad77eb888c。
- GitHub Windows CI：116 项离线回归、INI 检查、接口检查、构建、程序启动、许可与对应源码准备全部通过：https://github.com/ha7rock/JustDLSS5/actions/runs/35327886125
- 附件摘要、包内许可、BUILD-INFO 提交与工作流 ID 校验通过：https://github.com/ha7rock/JustDLSS5/actions/runs/35328166334
- PR #7 已合并，合并后文件树与通过检查的候选一致：https://github.com/ha7rock/JustDLSS5/pull/7
- v0.2.14 已于 2026-09-18T09:12:53Z 发布；非草稿、prerelease，四份附件齐全：https://github.com/ha7rock/JustDLSS5/releases/tag/v0.2.14
- Windows ZIP SHA-256：c74d503c020ac788dbf1248e79dd12b92d374ef03dd353658a427b7bbeae02b3
- 源码 ZIP SHA-256：36fdb950321dbdfa6d84d948246f1b6003441c1ada08eafa111ec362ecfba6f8
- README 中英文版本与下载入口、启动器已更新。游戏库 PR #5 仍独立，未覆盖原开发目录和用户修改。
- 未运行真实游戏安装、卸载、自动试装或 VR 实测；发行说明明确其验证限制。

本次维护执行已结束，无待完成的发布步骤。保留日程，不将维护任务混入后续普通对话。
