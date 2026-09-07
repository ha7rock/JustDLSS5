# 上游、下载来源与独立维护

本文基于本仓库固定的上游代码：`Kizzuwatnaa/DLSS5-Autopilot`，提交 `23f96c64ef5605f4700391adfb0cf7cf630cc40a`（1.6.1）。下载服务和第三方发行版本可能变化；下面描述的是代码使用的来源，不代表我们验证了每个远端文件。

## 原项目做了什么

原项目是安装与配置工具。它扫描本机游戏、识别图形 API 和显卡，选择组件组合，再下载、备份、复制文件和生成配置。DLSS 模型、ReShade、插件和 Remix 游戏模组大多由其他项目提供。

作者维护了组件来源、版本选择、兼容性规则和部分游戏对应的模组目录。这些编排和安装逻辑是原项目的重要贡献。不能把它理解成所有资源都是作者制作的，也不能把本项目前端理解成新的 DLSS 实现。

| 内容 | 实现位置 | 来源与维护方式 |
| --- | --- | --- |
| 游戏列表 | `core/games.py` | 读取本机平台清单、注册表和游戏目录；不是作者提供的云端游戏库 |
| 游戏图标 | `frontend/icons.py` | 从本机 EXE 或 ICO 提取；不下载游戏美术资源 |
| 图形 API、显卡与路线判断 | `core/dlss.py`、`core/gpu.py`、`core/installer.py` | 本地检测，加上上游维护的选择与兼容性规则 |
| 下载地址与版本选择 | `core/sources.py` 等 | 代码中的 GitHub 仓库、发行接口及网站地址 |
| Remix 游戏模组目录 | `core/remixlist.py` | 上游编排的游戏与第三方模组链接；模组资源属于各自作者 |
| 安装、备份、卸载 | `core/installer.py` 等 | 在用户机器上执行；不依赖原作者的在线安装服务 |

## 主要下载来源

这些组件按所选功能下载，不会全部预装在桌面程序里。

| 组件 | 代码指定的项目或站点 |
| --- | --- |
| ReShade | [reshade.me](https://reshade.me)，着色器头文件来自 [crosire/reshade-shaders](https://github.com/crosire/reshade-shaders) |
| Feeder | [jlrouzies-fr/DLSS5-Feeder](https://github.com/jlrouzies-fr/DLSS5-Feeder) |
| LumeniteFX | [umar-afzaal/LumeniteFX](https://github.com/umar-afzaal/LumeniteFX) |
| 部分 RenoDX 与 NVIDIA 运行库资源 | [RankFTW/rhi-repo](https://github.com/RankFTW/rhi-repo)，这是第三方汇集来源，不能统一称为原厂下载 |
| Bridge | [NIGos/dlss5-bridge](https://github.com/NIGos/dlss5-bridge) |
| Neural Upstream | [matiasLombo/neural-upstream](https://github.com/matiasLombo/neural-upstream) |
| Standalone | [kibblerz/DLSS5-Reshade-AIO](https://github.com/kibblerz/DLSS5-Reshade-AIO) |
| OptiScaler DLSS-NR | [Dagherbou/OptiScaler_DLSSNR](https://github.com/Dagherbou/OptiScaler_DLSSNR) |
| DXVK | [doitsujin/dxvk](https://github.com/doitsujin/dxvk) |
| Remix 运行库 | [lunks/dxvk-remix-plus-dlssnr](https://github.com/lunks/dxvk-remix-plus-dlssnr) |
| 视频工具 | [MPC-HC](https://github.com/clsid2/mpc-hc)、[yt-dlp](https://github.com/yt-dlp/yt-dlp)、[FFmpeg 构建](https://github.com/BtbN/FFmpeg-Builds)、[video2dlssnr](https://github.com/DaniilSokolyuk/video2dlssnr)、[Deno](https://github.com/denoland/deno) |

完整来源以 `core/sources.py`、`core/optiscaler.py`、`core/dxvk.py`、`core/reengine.py`、`core/video.py` 和 `core/remixlist.py` 为准。

## 文件写到哪里

| 内容 | 默认位置 |
| --- | --- |
| 下载缓存 | `%LOCALAPPDATA%\dlss5-autopilot\cache` |
| 发行接口缓存 | `%LOCALAPPDATA%\dlss5-autopilot\api-cache` |
| 游戏组件 | 检测到的游戏安装目标，通常是所选 EXE 的目录；已有安装记录可能指定其他根目录 |
| 游戏安装记录 | 目标目录中的 `dlss5-autopilot.json` |
| 原文件备份 | 目标目录中的 `.dlss5-autopilot-backup` |
| 视频播放器 | 默认 `用户目录\Videos\DLSS5 Player`，可另选目录；辅助工具在该目录的 `tools` 下 |
| ReShade Vulkan 层 | `%LOCALAPPDATA%\dlss5-autopilot\reshade-vulkan`，并注册到当前用户的 `HKCU\Software\Khronos\Vulkan\ImplicitLayers` |

Vulkan 层是当前用户范围的设置，可能影响其他 Vulkan 程序，因此不能宣称所有修改都只发生在一个游戏目录内。保留现有缓存目录名是为了兼容原有安装与设置。

## 能否独立维护

可以独立维护工具，但仍要维护第三方组件的兼容性。

- 本仓库包含固定版本的 `core/`，启动和日常操作不需要从原作者仓库加载业务代码。原作者停止更新不会让已经复制的代码消失。
- 上游代码采用 MIT 许可证；保留版权与许可证后可以继续修改和发布。MIT 不会自动授权重新分发第三方插件、游戏资源或 NVIDIA 运行库；这些内容各自适用自己的条件。
- 前端通过 `frontend/backend.py` 和服务层调用业务模块。`tools/update_backend.py` 在临时目录检查候选版本，检查通过后才允许应用，并保留备份。接口检查和回归测试可以发现部分不兼容，无法保证未来任意业务变更都无需适配。
- 下载站点、第三方发行接口、组件文件名及兼容性规则仍是外部依赖。如果来源失效，需要我们替换地址、核实授权、更新安装逻辑并实际测试。
- 原作者主要提供代码与编排，并不是一个必须持续付费或在线连接的私有后台。独立发展的成本主要是持续测试与维护，不是重建他的服务器。

## 后续需要补齐的维护能力

当前下载缓存主要依靠 HTTPS、文件存在与大小等条件，不能视作对所有组件进行了可信哈希校验。公开维护时应逐步建立固定版本清单、可信摘要、来源变更审查和真实游戏回归记录。

本项目前端测试覆盖控件与部分服务逻辑，不等于每个游戏、显卡和第三方插件组合都经过实测。反作弊提示是风险提示，不能保证未标记的游戏允许注入插件。
