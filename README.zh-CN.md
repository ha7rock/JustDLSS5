<p align="center">
  <img src="docs/images/app-icon.png" alt="JustDLSS5" width="96" height="96">
</p>

<h1 align="center">JustDLSS5</h1>

<p align="center"><strong>DLSS 5，少一点折腾。</strong></p>

<p align="center">
  Windows 上用的桌面工具：扫游戏、装画面组件、<br>
  管 DLSS 5 相关配置。界面是 Qt（PySide），中文英文都能切。
</p>

<p align="center">
  <strong>v0.2.4 · 玩家测试版</strong> · 安装核心来自 DLSS5-Autopilot <strong>v1.7.1</strong>
</p>

<p align="center">
  <a href="./README.md">English</a> ·
  <a href="#下载">下载</a> ·
  <a href="#能做什么">功能</a> ·
  <a href="#先看清楚">注意</a> ·
  <a href="#致谢与许可">许可</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-0.2.4-blue" alt="version 0.2.4">
  <img src="https://img.shields.io/badge/status-player%20preview-orange" alt="player preview">
  <img src="https://img.shields.io/badge/platform-Windows%20x64-lightgrey" alt="Windows x64">
  <img src="https://img.shields.io/badge/engine-Autopilot%20v1.7.1-informational" alt="Autopilot v1.7.1">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT">
</p>

---

## 下载

去 [Releases](https://github.com/ha7rock/JustDLSS5/releases) 下 Windows x64 包：`JustDLSS5-v0.2.4-windows-x64.zip`。

1. 整包解压到一个能写的文件夹。
2. 运行 `JustDLSS5.exe`。同目录的 `_internal` 和许可文件别删，别只拷一个 EXE。
3. 这个便携包不用单独装 Python。
4. 想核对文件可看 `SHA256SUMS.txt`。PowerShell：`Get-FileHash <文件> -Algorithm SHA256`。

同版本还有：`BUILD-INFO.json`（这次是怎么打出来的）、`JustDLSS5-v0.2.4-source-materials.zip`（程序和依赖的对应源码）。

怎么测、注意什么：[玩家测试说明](docs/TESTING-PREVIEW.zh-CN.md)。有问题：[提 Issue](https://github.com/ha7rock/JustDLSS5/issues/new?template=bug-report.yml)，或用应用里的「反馈问题」。

> 社区做的玩家测试版，不是稳定版，也跟 NVIDIA 没关系。

---

## 截图

| 中文界面 | 英文界面 |
| --- | --- |
| ![游戏库 · 中文](docs/images/library.zh-CN.png) | ![游戏库 · 英文](docs/images/library.en.png) |

*图里的游戏是演示数据，不是真实库存。*

---

## 为什么做这个

自己配 DLSS 5 相关组件，经常要找包、对 API、改路径，很容易踩坑。[DLSS5-Autopilot](https://github.com/Kizzuwatnaa/DLSS5-Autopilot) 那边已经把安装流程做好了；JustDLSS5 在上面做了独立桌面界面，扫库、选方案、预览变更、卸载还原，都可以在窗口里完成。

| | 自己折腾 | DLSS5-Autopilot | **JustDLSS5** |
|---|---|---|---|
| 界面 | 没有 | 上游自己的工具 | 独立 Qt（PySide）桌面程序 |
| 语言 | — | 上游 | 中文 / 英文 |
| 游戏库 | 自己找 | 上游流程 | 扫本机、手动加目录、看安装状态 |
| 安装核心 | 自己搞 | 上游 | 目前用 Autopilot **v1.7.1**（`core/`） |
| 维护 | 手工 | 上游 | 预览、诊断、卸载、还原备份 |
| 下载 | — | 上游 | 玩家测试 ZIP、校验摘要、许可和源码包 |

---

## 能做什么

**安装和游戏库**
- 识别游戏环境，给出可装方案
- 下载并配置组件；动手前可以先预览会改什么
- 扫描本机游戏，或自己加目录；看看哪些已经装过

**配置和维护**
- 调参数，保存和载入配置
- 出问题可以诊断；也能卸载，或从备份还原

**按游戏记**
- 图形 API 可以手动选，并按游戏记住
- 条件合适时，有 FSR 补帧、RTX 40 MFG 相关选项

**用起来**
- 中文 / 英文界面，窗口能缩放
- 后台任务会在你点的那个按钮上转进度
- 应用里能直接反馈问题（会带上版本和当前游戏）
- 检查更新只会打开发布页，**不会**自动覆盖程序

**另外还有**
- 屏幕 / 窗口捕获（和摄像头共用开始、停止）
- 视频增强、RTX Remix 相关工具

**安全相关**
- 带反作弊的游戏，安装或批量重装前会再问一次（默认是取消）
- 就算没弹警告，也不代表这个游戏一定允许装插件

---

## 和 DLSS5-Autopilot 差在哪

| | DLSS5-Autopilot | JustDLSS5 |
|---|---|---|
| 做什么 | 上游的安装引擎 / 工具 | 在这套逻辑上的桌面界面 |
| 版本 | 跟着上游发 | 现在固定在 **v1.7.1**（见 `backend-version.json`） |
| 界面 | 上游 | 自己做的 Qt，中英双语 |
| 给玩家的包 | 上游项目 | 便携 ZIP、SHA-256、构建信息、许可和源码 |
| 许可 | 上游 | JustDLSS5 代码是 MIT；上游版权照样保留 |

安装相关代码在 `core/`。细节见 [上游与来源](docs/UPSTREAM-AND-SOURCES.zh-CN.md)、[上游 README](docs/UPSTREAM_README.md)。这个测试版**还没有**上游 v1.7.2 的新东西。

---

## 先看清楚

- 界面、衔接、命令行、打包启动有自动检查。**没有「已兼容游戏名单」**；没写过的组合，就当没测过。
- 第一次建议先拿**离线单机**试。装之前自己备份存档和重要配置。工具做的组件备份，不能当完整备份用。
- 反作弊提示不完整；**没警告不等于安全**。别拿联网或反作弊游戏去试会不会封号。
- 组件要从第三方站点下。下失败了，不一定是游戏不兼容，把任务日志留着。
- 程序还没做商业签名。SHA-256 只说明文件没下坏，不代表「安全认证」。
- 测试版，难免有小问题。能复现的话，麻烦按步骤反馈。

更细的说明：[玩家测试说明](docs/TESTING-PREVIEW.zh-CN.md)。

**显卡**（按 `docs/` 里上游 / 社区说法整理，不是我们测出来的帧数）
- 上游工具对 RTX 50 / 40 / 20–30 有对应路径
- GTX，以及比 RTX 20 更早的卡，跑不了
- 这是非官方、还在变的生态；这里不写「能提升多少帧」

---

## 从源码跑

给要改代码的人（Windows x64、Python 3.12）：

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-desktop.txt
python autopilot_desktop.py
```

```bat
build-desktop.bat
```

打出来在：`dist/v0.2.4/JustDLSS5/JustDLSS5.exe`，旁边的 `_internal` 要留着。

维护说明：[docs/MAINTAINING.zh-CN.md](docs/MAINTAINING.zh-CN.md)。

---

## 致谢与许可

**致谢**
- 安装核心：[Kizzuwatnaa/DLSS5-Autopilot](https://github.com/Kizzuwatnaa/DLSS5-Autopilot)
- 还会用到生态里的组件，比如 ReShade、RenoDX、Feeder、OptiScaler、DXVK、RTX Remix 等。名单见 [第三方声明](docs/THIRD-PARTY-NOTICES.md)、[上游与来源](docs/UPSTREAM-AND-SOURCES.zh-CN.md)

**许可**
- JustDLSS5 自己的代码：**MIT**
- 从 Autopilot 来的部分，请保留上游版权
- 第三方组件、NVIDIA 运行时、游戏 mod 各有各的许可。源码仓库不带这些二进制；便携包里另有依赖许可说明

---

## 文档

- [玩家测试说明](docs/TESTING-PREVIEW.zh-CN.md)
- [v0.2.4 说明](docs/RELEASE-v0.2.4.md)
- [第三方声明](docs/THIRD-PARTY-NOTICES.md)
- [维护说明](docs/MAINTAINING.zh-CN.md)
- [上游与来源](docs/UPSTREAM-AND-SOURCES.zh-CN.md) · [上游 README](docs/UPSTREAM_README.md)

---

<p align="center">JustDLSS5 · v0.2.4 玩家测试版 · MIT · 社区工具，跟 NVIDIA 没关系</p>
