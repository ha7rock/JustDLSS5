# JustDLSS5 v0.2.13 · 玩家测试版 / Preview

安装核心更新至 DLSS5-Autopilot v1.9.0（c3bab6da10fbb70cefb03f70464ca876a07316b0）。

- 更多操作增加实验性自动路线尝试：开始前明确确认安装、启动、读取已加载组件及后续路线尝试；支持停止，反作弊检测失败或发现风险时拦截。
- 运行分析展示当前机器日志推算的模型开销；不把模型耗时当作游戏帧率。配置与日志不一致时不生成估算。
- 社区报告补充实测数据；不会自动上传。继承 DLSS 替换版本信息、安装记录、诊断修复和 Elytra 反作弊识别。
- 保留设置说明与 750 毫秒悬停帮助；游戏库改版仍在独立 PR，本版不包含。

完整解压 Windows x64 ZIP 到新目录后运行 JustDLSS5.exe，无需 Python。附第三方许可、对应源码材料、SHA256SUMS.txt 与 BUILD-INFO.json。

本轮验证为离线回归、临时文件夹具及 Windows 启动验证，未执行真实游戏安装、自动路线试装或 VR 测试。实验性自动尝试可能在同次确认后继续安装下一条路线，停止需等待当前安装结束，不会自动卸载。请勿用于联网或反作弊游戏。社区项目，与 NVIDIA 无关。

## English

Updates the pinned engine to Autopilot v1.9.0. Adds explicitly confirmed, cancellable experimental route trials with anti-cheat gates, session model-cost estimates, measured community guidance and updated diagnostics. Keeps the existing interface and hover help; the library redesign remains in its separate PR.

Extract the complete Windows ZIP into a new directory. Dependency licenses, corresponding source materials, checksums and build metadata are included. Validation is offline and packaged startup only, with no real-game route trials or VR validation. Route trials can install subsequent routes after one explicit confirmation; stopping waits for an ongoing installation. Avoid online and anti-cheat games. Not affiliated with NVIDIA.
