# JustDLSS5 维护说明

产品介绍与使用方法见 [README](README.md)。

## 更新安装引擎

前端使用仓库中的固定版本 `core/`，版本记录在 `backend-version.json`。不要用上游 EXE 覆盖 JustDLSS5。

先检查候选版本：

```powershell
.venv/Scripts/python.exe tools/update_backend.py <版本标签或提交>
```

默认只检查，不替换代码。工具从原项目获取指定版本，在临时目录运行接口与界面测试。检查通过后，关闭程序，再应用并重新打包：

```powershell
.venv/Scripts/python.exe tools/update_backend.py <版本标签或提交> --apply
./build-desktop.bat
```

更新只替换 `core/`，旧版本保存在 `backend-backups/`。如果上游删除接口、修改参数或返回结构，需要调整适配层。自动检查不能代替真实游戏兼容性测试。

## 检查与测试

```powershell
.venv/Scripts/python.exe tools/check_backend.py
.venv/Scripts/python.exe test_ui.py
.venv/Scripts/python.exe test_cli.py
.venv/Scripts/python.exe test_reshade_ini.py
```

界面测试使用临时设置与模拟游戏数据，不安装真实组件。上游的完整安装测试依赖特定游戏和资源；不能把离线测试通过理解为所有游戏已实测。

构建使用 Qt Widgets 和目录分发，避免每次启动解压完整运行库。发布包需同时包含第三方许可与对应源码获取说明；构建成功本身不代表发布检查已完成。

## 维护原则

- 业务调用集中到适配层；不为改文案修改 `core/`。
- 绘制、排序和搜索不读取磁盘，耗时操作进入后台任务。
- 修复问题时增加能复现问题的回归用例，避免仅验证实现细节。
- 文案说明操作及结果；不使用无依据的性能、兼容性或“一键成功”承诺。
- 新功能附实际验证范围，保留原作者和第三方组件归属。

## 源码结构

| 位置 | 职责 |
| --- | --- |
| `frontend/desktop.py` | 页面布局与交互协调 |
| `frontend/controls.py`、`theme.py`、`library.py` | 控件、样式与列表模型 |
| `frontend/service.py`、`backend.py` | 业务适配与上游导入边界 |
| `frontend/jobs.py`、`icons.py` | 后台任务与本地图标读取 |
| `frontend/about.py` | 产品名称、版本与项目链接 |
| `core/` | 固定版本的上游安装引擎 |
| `tools/` | 接口检查、更新与打包工具 |

前端与业务代码分开维护。上游更新不会直接覆盖界面；接口变化仍需适配和测试。参见 [维护说明](README.zh-CN.md)。