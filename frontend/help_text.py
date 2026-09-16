"""Short explanations of outcomes and tradeoffs, grouped by user decision."""

HELP = {
    "route": (
        "选择游戏接入神经渲染的方式，影响兼容性和可用功能。优先使用推荐路线；出现无效果或崩溃时再排查。",
        "Chooses how neural rendering connects to the game, affecting compatibility and available features. Start with the recommended route; investigate alternatives if it fails to load or crashes.",
    ),
    "quality": (
        "画质方案会一起调整相关参数。降低渲染区域可减少处理开销，但细节可能变软。目标帧率用于游玩后的分析建议，不是锁帧，也不保证达到该帧率。",
        "Profiles adjust related settings together. A smaller work area reduces processing cost but can soften detail. Target FPS guides analysis after playing; it is neither a frame limiter nor a performance guarantee.",
    ),
    "target": (
        "选择实际运行的游戏程序及图形接口，确保组件装到正确位置。通常保留自动检测；程序架构仅在 Windows 限制读取时手动选择。这些设置不会直接提高画质。",
        "Identifies the actual game executable and graphics API so components go in the right place. Usually keep automatic detection; choose architecture manually only for protected executables. These settings do not directly improve image quality.",
    ),
    "frames": (
        "补帧增加显示帧数，让画面更流畅，但可能增加延迟或伪影。FSR 2x 要求 OptiScaler / DX12，并关闭游戏原有补帧；RTX 40 MFG 另有显卡和路线限制。",
        "Frame generation adds displayed frames for smoother motion, with possible latency or artifacts. FSR 2x requires OptiScaler / DX12 and in-game frame generation off. RTX 40 MFG has separate GPU and route requirements.",
    ),
    "feed": (
        "这些参数供 Feeder 使用：运动矢量帮助跟踪画面运动，错误来源可能造成拖影；DLSS 预设和 HDR 控制处理方式。通常保留默认，它们不是 OptiScaler 的模型设置。",
        "These are Feeder settings: motion vectors track movement, and a wrong source can cause ghosting. DLSS preset and HDR select processing behavior. Usually keep defaults; these are not OptiScaler model settings.",
    ),
    "model": (
        "NR 模型与风格用于 OptiScaler，调整神经渲染的预设和视觉风格。它们不是从低到高的画质等级；可比较实际画面后按喜好选择。",
        "NR model and style select OptiScaler neural-rendering presets and visual styles. They are not ranked quality levels; compare the resulting image and choose your preference.",
    ),
    "loading": (
        "加载名称决定游戏如何找到插件，分支决定使用哪个 OptiScaler 实现。通常保留自动或默认；主要用于解决插件冲突、无法加载或特定游戏的兼容问题。",
        "The proxy name determines how the game loads a plug-in; the build selects an OptiScaler implementation. Usually keep automatic or default choices. Change them to address conflicts, loading failures or game-specific compatibility issues.",
    ),
    "optional": (
        "OpenXR 用于受支持的 VR 路线，DXVK 转换图形接口，Remix 替换用于对应的 Remix 游戏。它们有各自的适用条件，并非通用画质增强；OpenXR 注册会影响其他 OpenXR 应用。",
        "OpenXR serves supported VR routes, DXVK translates graphics APIs, and Remix replacement is for applicable Remix games. Each has specific requirements; they are not general quality boosts. OpenXR registration affects other OpenXR apps.",
    ),
    "versions": (
        "通常使用自动／推荐版本。更新组件可能修复问题，也可能改变兼容性；版本号更高不代表画质更好。需要复现或解决特定问题时才固定版本或使用本地插件，且只对使用该组件的路线生效。",
        "Usually use automatic or recommended versions. Updates may fix issues or change compatibility; a higher version is not necessarily better-looking. Pin a version or use a local add-on for a specific issue, and only on routes that use that component.",
    ),
}


def explanation(key, chinese):
    return HELP[key][0 if chinese else 1]
