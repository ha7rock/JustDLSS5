# v1.9.0 接入记录

触发：2026-09-16 10:01（Asia/Shanghai），justdlss5 自动任务。
上游：v1.9.0，固定提交 c3bab6da10fbb70cefb03f70464ca876a07316b0。
公开基线：JustDLSS5 v0.2.9 / Autopilot v1.8.2。
维护分支：codex/upstream-1.9-release；不合并游戏库 PR #5。

## 接入与边界

- diagnose.py 拆分为 diagnose 包；前端静态文案检查覆盖包内模块。
- 新增 autopilot/watch：提供明确确认页面、最多三条路线、取消等待当前安装结束；前端再次检查反作弊和路线支持，不自动启动测试。
- autotune：使用可追溯到日志的配置比例；不匹配时不输出估算。模型耗时与 FPS 分别展示，不把模型耗时当游戏帧率。
- community：显示实测起点，分享仍经用户操作。
- 继承 DLSS 替换版本、安装记录、诊断和 Elytra 反作弊识别。
- 依赖与下载来源由固定上游继承；未增加 Python 依赖。Qt/Python/certifi 许可与对应源码仍按发布工具打包。
- 保留未发布的帮助交互修复，不自动安装、启动真实游戏、写全局图形层或修改仓库可见性。

## 验证与发布

状态：已完成接入、验证与玩家测试版发布，详见下方执行结果。
离线测试不能确认自动试装在真实游戏中的稳定性；无 GPU/VR 实测声明。

### 本次执行结果（2026-09-16 自动触发）

- 固定提交接入完成；115 项接口检查、107 项本地回归、INI 检查和 Windows 打包启动通过。
- GitHub Windows CI 完成依赖安装、回归、构建、启动、许可及对应源码准备：https://github.com/ha7rock/JustDLSS5/actions/runs/35046835805
- 附件摘要、BUILD-INFO 提交、工作流 ID、包内许可校验通过：https://github.com/ha7rock/JustDLSS5/actions/runs/35047034591
- 维护 PR #6 已合并；构建与发行标签对应 baa666e85a00ca2e89520ef53f708fa1227ec435。
- 已发布 v0.2.13（非草稿，prerelease）：https://github.com/ha7rock/JustDLSS5/releases/tag/v0.2.13
- Windows ZIP SHA-256：96bc991f62e2b453c101e05d820d6ee93d0f5aad9429e51f94ab3a0e34edbe27
- 源码 ZIP SHA-256：e382ab72f551a9ff1ee09ebf393b3da57b217fbc9a1f2711b7eb82ad4f610d62
- README 中英文入口与启动器已指向 0.2.13。游戏库 PR #5 未合并，原开发目录未覆盖。
- 未执行真实游戏安装、自动路线试装或 VR 实测，发行说明已明确。

本次维护执行已结束，无待完成的发布步骤。保留日程，不将本次维护视为后续普通对话的当前任务。