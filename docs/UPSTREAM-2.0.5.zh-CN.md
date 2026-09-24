# 上游 v2.0.5 接入记录

## 触发与基线

2026-09-24T09:31:07.307Z，automation_id=justdlss5 自动触发。普通界面优化讨论不是触发来源。
远端 main 为 2904f47960a50b8dafb4d7cb9b49033ac190a625，已发布产品 v0.2.14 / 引擎 v2.0.1（39e5e2b323482b9639b31d0b5589aa6febed6eb4）。
检查的最新正式版为 v2.0.5，发布于 2026-09-22T20:46:25Z；标签解析为固定提交 cc9a94187fabe2754ec913cc8eca481b56f2082a。
本次在 codex/upstream-2.0.5-release 独立工作树进行，保留原目录、游戏库 PR #5 和其他远端修改。

## 差异与接口适配

比较包含 181 个提交，覆盖 v2.0.2–v2.0.5。核心及 CLI 按固定提交完整接入，未编辑上游核心。

- 安装：链接路径备份修复；OptiScaler 只选真正的组件包，先验证归档包含组件再写入；Feeder 稳定版选择同时检查标签，避免 GitHub 预发布标志错误；这些从核心继承。
- 新增 core.child 清理外部程序继承的 PyInstaller DLL 搜索路径与环境；自动试装、视频工具使用上游新调用，Qt 仍排除 Tk 模块。
- 游戏/API：模拟器后端修正、Unreal 1/2 渲染器读取、DX8 经 DXVK。Qt 原有 games.enrich 与 APIS 动态枚举继承修复。
- OptiScaler 新增 PRESR_MFG、card_refusal、is_presr 等。Qt 增加中文标签和使用条件，已知非 RTX 40 禁用；安装核心会在卸除旧路线前再次拒绝不支持的显卡，不自动选择该变体。
- components.Item.note 新增缺代理与误装测试版原因。Qt 逐条翻译，保留未知原文，取消原先将所有 OptiScaler note 归为错包的处理。
- 诊断新增静态文案已翻译。Qt session 适配上游 Tk 控制器中的退出阶段异常规则（时间窗口、末尾卸载标记、先释放功能再释放参数），不引入 Tk 依赖；原始记录和界面都区分退出异常与运行中崩溃。
- diagnose.answered 接入“检查安装与运行”的补充入口，未启动/自行退出后在后台重算建议，保留证据；取消不改变结果，不自动执行建议。
- community.record 新增 said_by、verdicts.outcome 区分未知与失败。Qt 当前读取上游社区汇总，不自动写入上游结果；不会用日志不可见推断失败并上传。上游聚合工作流位于上游仓库，不在本项目复制。
- 上游 Tk 侧栏与海报墙调整不替换本产品界面；独立游戏库 PR 继续保留。

## 下载、依赖与验证

新增 OptiScaler 变体仍来自 wilsjo2 原仓库；其他下载来源继承固定核心。没有新增 Python 依赖；Qt/PySide/Python/certifi 许可及对应源码按既有发行流程准备并校验。

首次隔离检查发现新增诊断翻译缺失与旧测试伪造包名不符合新包校验规则；修正后固定提交接入通过。122 项离线回归与 INI 检查通过，包含错误包与变体筛选、显卡限制、退出异常时序、用户补充取消和外部进程启动失败后的 DLL 路径恢复。

本次未安装、卸载、启动真实游戏或写入全局图形层；无新增显卡组合、DX8 或 VR 的实机兼容性声明。

状态：接入、验证与玩家测试版发布已完成。


## 执行结果（2026-09-24 自动触发）

- 132 项后端属性/调用检查、122 项离线回归及 INI 检查通过；76 个核心/CLI 文件与固定上游一致。
- 本地 Windows 打包和程序启动通过。
- 独立 Windows CI 完成回归、构建、启动、许可和对应源码准备：https://github.com/ha7rock/JustDLSS5/actions/runs/35982980054
- 构建提交、工作流 ID、包内许可和发行摘要校验通过：https://github.com/ha7rock/JustDLSS5/actions/runs/35983292989
- PR #8 已合并，合并后文件树与候选一致：https://github.com/ha7rock/JustDLSS5/pull/8
- 构建与发行标签提交：cca9257417466ddb79092e1704c3a31bcd8e7cfa。
- v0.2.15 已于 2026-09-24T09:47:44Z 发布，非草稿、prerelease，程序、源码、摘要和构建信息四份附件齐全：https://github.com/ha7rock/JustDLSS5/releases/tag/v0.2.15
- Windows ZIP SHA-256：6416739dcb16c0853c9c32ba55f2af4c701439c0631457610195e565f749da58
- 源码 ZIP SHA-256：cff6d89f4ae288f35447a34edd8c4dcf8b19c0eb8ad3e75a44c0c718ac194ad8
- 中英文 README 版本与下载入口、启动器同步至 v0.2.15。未覆盖原开发目录，未合并独立游戏库设计 PR。

本次维护执行已结束，无待完成的发行步骤。保留日程，不把维护任务混入后续普通对话。
