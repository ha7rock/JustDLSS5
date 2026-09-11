"""Presentation-only translations for the pinned engine's diagnostic messages.

Match complete messages, never replace words inside paths or captured log text.
Unknown upstream messages remain visible in the original language. Updating the
engine should include reviewing this catalog; no diagnosis is inferred here.
"""
import re


_MESSAGES = r"""
Working.|神经渲染已运行。
Every DLSS evaluate faults inside NVIDIA's NGX runtime (D3D12Core.dll <- nvngx_dlssnr.dll <- _nvngx.dll <- renodx-dlss5).|每次 DLSS 求值均在 NVIDIA NGX 运行库内发生异常（D3D12Core.dll ← nvngx_dlssnr.dll ← _nvngx.dll ← renodx-dlss5）。
On 32-bit the DLSS 5 page in the game's overlay drives the 64-bit helper; the helper's own window is there too, but do not alt-tab to it while playing - that minimizes the game and tears the feature down.|32 位游戏通过游戏浮层中的 DLSS 5 页面控制 64 位辅助进程。游玩时不要切换到辅助进程窗口，否则游戏会最小化并中断渲染功能。
OptiScaler needs driver 616.56 or newer, and a nvngx_dlssnr build for your card (the tool picks one). If it keeps refusing, the native or renodx-dlss route is one click away.|OptiScaler 需要 616.56 或更新驱动，以及匹配显卡的 nvngx_dlssnr 版本。如果仍被拒绝，可尝试 Native 或 renodx-dlss 路线。
OptiScaler runs the model around the game's own upscaler. Turn DLSS (or FSR/XeSS) on in the game's graphics menu and set it to anything but 'off' - with no upscaler running there is nothing for neural rendering to attach to, which is what the overlay means by 'waiting for the upscaler to run'. If the game has no upscaler at all, use the feeder route.|请先在游戏画面设置中开启 DLSS、FSR 或 XeSS。OptiScaler 依赖游戏的超分功能；未开启时，浮层会提示等待超分运行。如果游戏没有超分选项，请使用 Feeder 路线。
Add-on support requires the ReShade build WITH add-ons, and AddonPath must point at the game folder.|需要使用支持插件的 ReShade 版本，并将 AddonPath 指向游戏目录。
Check the ReShade overlay for a compile error and that reshade-shaders\Shaders holds DLSS5_Feed.fx.|请在 ReShade 浮层中检查编译错误，并确认 reshade-shaders\Shaders 中存在 DLSS5_Feed.fx。
If you were moving, the provider is producing nothing and you will see smearing.|如果游戏画面当时在移动，说明运动矢量来源未产生有效数据，可能出现拖影。
Its log says 'required private runtime dependency missing': nvngx.dll (the caller bridge) as well as the add-on, plus nvngx_dlssnr.dll and nvngx_dlss.dll, must all sit beside the executable. Installing again puts every one of them back; antivirus quarantine is the usual reason one is gone.|请检查游戏可执行文件旁是否有插件、nvngx.dll、nvngx_dlssnr.dll 和 nvngx_dlss.dll。重新安装会补齐文件；也可先检查安全软件的隔离记录。
Loaded and set up; no neural frame yet.|插件已加载并完成配置，尚无神经渲染帧。
Set up, no frame through yet.|已完成配置，尚未记录到处理后的画面。
Set up correctly, but not switched on yet.|配置正常，尚未开启神经渲染。
DLSS never started.|DLSS 尚未启动。
OptiScaler.ini is missing - install again.|缺少 OptiScaler.ini，请重新安装组件。
OptiScaler's log is off - install again to switch it on, then play once.|OptiScaler 日志未开启。请重新安装组件，再运行一次游戏。
Not run yet, or OptiScaler did not load.|尚未运行游戏，或 OptiScaler 未加载。
OptiScaler is not in the game folder - install again.|游戏目录中没有 OptiScaler，请重新安装组件。
The game is on Vulkan; the optiscaler route needs a Direct3D renderer - or use the feeder route.|游戏使用 Vulkan；OptiScaler 路线需要 Direct3D。可切换游戏渲染接口，或改用 Feeder 路线。
The game refused OptiScaler's swapchain - try another name in 'loads as', or the feeder route.|游戏拒绝了 OptiScaler 的交换链。可更换加载文件名，或尝试 Feeder 路线。
Neural rendering stopped after it started.|神经渲染启动后停止了。
OptiScaler loaded, but the model refused or failed.|OptiScaler 已加载，但模型被拒绝或运行失败。
Neural rendering never ran - the game's own upscaler has to be on for this route.|神经渲染未运行。这条路线需要先在游戏内开启 DLSS、FSR 或 XeSS。
OptiScaler loaded; neural rendering not switched on.|OptiScaler 已加载，神经渲染尚未开启。
No Remix runtime in the folder any more.|游戏目录中已找不到 Remix 运行库。
The Remix runtime here has no neural pass - use the swap option.|当前 Remix 运行库不支持神经渲染，请使用运行库替换选项。
Not run yet, or the Remix runtime never loaded.|尚未运行游戏，或 Remix 运行库未加载。
Remix ran, but the DLSS 5 snippet never started.|Remix 已运行，但 DLSS 5 模块未启动。
Remix ran; the neural pass was never even attempted.|Remix 已运行，但没有尝试启动神经渲染。
Inconclusive - open Alt+X -> Developer Settings Menu -> Post-Processing and read the Neural Uplift line.|日志不足以判断。请按 Alt+X，打开 Developer Settings Menu → Post-Processing，查看 Neural Uplift 状态。
DXVK is missing from the folder - reinstall.|游戏目录中缺少 DXVK，请重新安装组件。
Files the install wrote are gone from the folder - restore them and exclude the folder before reinstalling.|安装的部分文件已丢失。请先检查隔离记录并确认文件来源，再决定是否还原或重新安装。
Installed after the last run - play once and check again.|日志早于本次安装。请运行一次游戏后重新检查。
The install never finished - install again.|上次安装未完成，请重新安装组件。
The uninstall left files behind - close the game and uninstall again.|卸载后仍有文件残留，请关闭游戏后再次卸载。
The 32-bit Vulkan layer was being discarded as a duplicate name - install again to rewrite it.|32 位 Vulkan 层因重名未被加载，请重新安装组件以修复注册信息。
ReShade's Vulkan layer is not registered - install again.|ReShade Vulkan 层未注册，请重新安装组件。
The driver has no DLSS 5 entry point - update the graphics driver.|显卡驱动缺少 DLSS 5 接口，请更新驱动。
The add-on found no DLSS 5 entry point to hook - check the driver is 616.56 or newer.|插件未找到 DLSS 5 接口，请检查显卡驱动是否为 616.56 或更新版本。
DLSS never started - the add-on crashed creating the feature.|DLSS 未启动：插件在创建功能时崩溃。
The crash is in the game's own code - no add-on in the stack.|崩溃堆栈位于游戏代码中，未发现插件调用。这不能单独证明插件与崩溃无关。
The crash is in the graphics runtime, not in the feed - try another DLSS 5 add-on build.|崩溃堆栈位于图形运行库。可尝试其他 DLSS 5 插件版本。
The feed crashed after starting - a feeder bug; try another feeder build.|Feeder 启动后崩溃，可尝试其他 Feeder 版本。
Frames flow, but neural rendering is silently doing nothing - old d3dcompiler_47.dll in the game folder.|画面在传递，但神经渲染未生效：游戏目录中的 d3dcompiler_47.dll 过旧。
The neural pass cannot compile - old d3dcompiler_47.dll in the game folder.|神经渲染无法编译：游戏目录中的 d3dcompiler_47.dll 过旧。
The bridge's substitute is off - install the bridge route again.|Bridge 的替代功能未开启，请重新安装 Bridge 路线。
Inconclusive - the feed did not get far enough to tell.|Feeder 日志不足，暂时无法判断运行结果。
The add-on runs but never produces a frame.|插件在运行，但尚未输出有效画面。
Neural rendering ran, then the add-on stopped at a device re-creation.|神经渲染曾运行，随后在重建图形设备时停止。
The game's DLSS call was never hooked - nothing to run on.|插件未接入游戏的 DLSS 调用，无法执行神经渲染。
Add-on loaded, but its own log has nothing yet - play once and check again.|插件已加载，但没有运行记录。请运行一次游戏后重新检查。
The add-on loaded but is missing a runtime file - reinstall.|插件已加载，但缺少运行库文件，请重新安装组件。
No NGX core in the driver - update the NVIDIA driver.|驱动中未找到 NGX 核心，请更新 NVIDIA 驱动。
The add-on's pipeline failed - see the stage it names.|插件处理流程失败，请查看下方记录的失败阶段。
Inconclusive - the add-on attached but built nothing.|插件已接入，但没有完成初始化，暂时无法判断运行结果。
The log predates the current install.|日志早于本次安装。
ReShade.log is older than the install.|ReShade.log 早于本次安装。
The Remix log predates the current install.|Remix 日志早于本次安装。
The standalone-dlssnr log predates this install.|standalone-dlssnr 日志早于本次安装。
Neural rendering is running.|神经渲染正在运行。
Neural rendering started.|神经渲染已启动。
Neural rendering did not start.|神经渲染未启动。
Neural rendering is switched off.|神经渲染未开启。
OptiScaler.ini is missing.|缺少 OptiScaler.ini。
OptiScaler's log is switched off.|OptiScaler 日志未开启。
OptiScaler loaded and found the neural-rendering forwarder.|OptiScaler 已加载，并找到神经渲染转发组件。
OptiScaler mentions neural rendering but never reports it running.|OptiScaler 日志提到了神经渲染，但没有运行证据。
OptiScaler ran, but neural rendering was never asked for.|OptiScaler 已运行，但未收到神经渲染请求。
No OptiScaler log from this install yet.|本次安装后尚无 OptiScaler 日志。
No OptiScaler log, and no proxy in the folder.|没有 OptiScaler 日志，目录中也没有代理文件。
Neural rendering was switched on, but the model never drew a frame.|神经渲染已开启，但模型尚未生成画面。
The game is drawing with Vulkan, and this route was installed for a Direct3D game.|游戏正在使用 Vulkan，而当前路线按 Direct3D 安装。
The RTX Remix runtime is gone from this game.|游戏目录中已找不到 RTX Remix 运行库。
This Remix runtime has no DLSS 5 neural pass.|当前 Remix 运行库不包含 DLSS 5 神经渲染。
Neural rendering is switched off in rtx.conf.|rtx.conf 中未开启神经渲染。
The Remix runtime has not written a log yet.|Remix 运行库尚未生成日志。
The runtime loaded nvngx_dlssnr.dll from the .trex folder.|运行库已从 .trex 目录加载 nvngx_dlssnr.dll。
The DLSS-NR snippet initialised.|DLSS-NR 模块已初始化。
Remix mentions DLSS-NR but never created the feature.|Remix 记录了 DLSS-NR，但没有创建对应功能。
The Remix runtime ran but says nothing about DLSS-NR.|Remix 已运行，但没有 DLSS-NR 记录。
ReShade's Vulkan layer is not registered any more.|ReShade Vulkan 层已失去注册信息。
The 32-bit ReShade layer carries the layer name the 64-bit one uses, so the Vulkan loader throws it away.|32 位 ReShade 层与 64 位层重名，Vulkan 加载器忽略了它。
DXVK ran, and ReShade did not.|DXVK 已运行，ReShade 未运行。
The install did not finish.|上次安装未完成。
The uninstall did not finish.|上次卸载未完成。
An old dlss5-feed.log is still in the folder.|目录中保留着旧的 dlss5-feed.log。
Two DLSS add-ons are loaded: ours and ShortFuse's renodx-dlss.|同时加载了当前 DLSS 插件和 ShortFuse 的 renodx-dlss。
Both the feeder and the bridge add-on are loaded.|Feeder 和 Bridge 插件同时加载。
ReShade attached to a Direct3D 9 device, not DXGI.|ReShade 接入的是 Direct3D 9 设备，而非 DXGI。
The game closed before it drew a single frame.|游戏在输出第一帧之前关闭了。
ReShade loaded no add-ons.|ReShade 没有加载插件。
The add-on flagged your nvngx_dlssnr as an untested build.|插件将当前 nvngx_dlssnr 标记为未经测试的版本。
ReShade skipped a device whose window is the desktop.|ReShade 跳过了窗口属于桌面的设备。
DLSS5_Feed.fx loaded and its textures were found.|DLSS5_Feed.fx 及其纹理已加载。
DLSS5_Feed.fx never loaded.|DLSS5_Feed.fx 未加载。
The 32-bit helper process started.|32 位游戏的辅助进程已启动。
The game and the helper are talking.|游戏与辅助进程已建立通信。
The helper started but never connected.|辅助进程已启动，但未建立连接。
Something else is pacing the frames this game presents.|另有因素在限制游戏的画面输出节奏。
NGX initialised successfully.|NGX 初始化成功。
The driver reports DLSS as available.|驱动报告 DLSS 可用。
The driver reports DLSS as NOT available.|驱动报告 DLSS 不可用。
NGX created the neural feature.|NGX 已创建神经渲染功能。
The feature was created but no frames were delivered.|功能已创建，但尚未传递画面。
If it is switched on and still does nothing, check the depth buffer.|如果已开启但仍无效果，请检查深度缓冲区。
The game's own d3dcompiler_47.dll is too old for the neural pass.|游戏自带的 d3dcompiler_47.dll 太旧，无法编译神经渲染。
The driver's NGX runtime does not export the call the add-on hooks.|驱动的 NGX 运行库未提供插件所需的接口。
The game hands the add-on no exposure value.|游戏没有向插件提供曝光值。
The add-on never found the game's DLSS call.|插件未找到游戏的 DLSS 调用。
The add-on loaded and set itself up, but never ran.|插件已加载并完成配置，但尚未运行。
The add-on has not written its own log yet.|插件尚未生成自己的运行日志。
The add-on found no private runtime beside it.|插件旁缺少所需的独立运行库。
The add-on found no NGX core in the NVIDIA driver.|插件未在 NVIDIA 驱动中找到 NGX 核心。
Motion vectors: VORT optical flow is feeding the network.|运动矢量：VORT 光流正在向模型提供数据。
Running on zero-motion guides - expect ghosting.|运动引导数据为零，可能出现拖影。
Frame generation is off: no usable nvngx_dlssg.dll.|帧生成未开启：缺少可用的 nvngx_dlssg.dll。
Frame generation failed and was switched off.|帧生成失败，已关闭。
The add-on's own output window could not be created.|无法创建插件的画面输出窗口。
Vulkan: the add-on is waiting for a shared frame.|Vulkan：插件正在等待共享画面。
The feature set was created but no frame was logged.|功能已创建，但没有画面处理记录。
The add-on attached but never reached a contract.|插件已接入，但未完成运行配置。
Motion vectors measured 0% non-zero.|运动矢量检测结果全部为零。
No depth in a video player - expected.|视频播放器未提供深度信息，属于预期情况。
ReShade is not giving the feed a depth buffer.|ReShade 没有向 Feeder 提供深度缓冲区。
Building the feed resources failed.|Feeder 资源创建失败。
This route leaves no frame log of its own.|当前路线不记录逐帧运行日志。
If the picture only gets darker, switch the route to native.|如果画面只是变暗，请尝试 Native 路线。
The bridge replaced the settings this install wrote.|Bridge 覆盖了本次安装写入的设置。
Or this log is from another program's ReShade.|这份 ReShade 日志也可能来自其他程序。
Two NGX hooks are loaded: neural-upstream and the renodx-dlss5 add-on.|neural-upstream 和 renodx-dlss5 同时接入了 NGX。
Two NGX hooks are loaded: the DLSS 5 add-on and neural-upstream.|DLSS 5 插件和 neural-upstream 同时接入了 NGX。
Two add-ons process the frame: standalone-dlssnr and the renodx-dlss5 add-on.|standalone-dlssnr 和 renodx-dlss5 同时处理画面。
Two add-ons process the frame: the DLSS 5 add-on and standalone-dlssnr.|DLSS 5 插件和 standalone-dlssnr 同时处理画面。
"""
MESSAGES = dict(line.split("|", 1) for line in _MESSAGES.strip().splitlines())

# Captures are inserted unchanged. Full matching avoids translating an excerpt
# from an unrelated message whose wording happens to share a prefix.
_PATTERNS = [
    (r"Driver 616\.64\+ faults inside NGX even with renodx-dlss5 (.+) - try the standalone route, or roll the driver back to 616\.56\.", "驱动 616.64 及更新版本在 renodx-dlss5 {0} 下仍出现 NGX 异常。可尝试 Standalone 路线，或回退至驱动 616.56。"),
    (r"Driver 616\.64\+ faults inside NGX even with renodx-dlss5 (.+) - roll the driver back to 616\.56\.", "驱动 616.64 及更新版本在 renodx-dlss5 {0} 下仍出现 NGX 异常，上游建议回退至驱动 616.56。"),
    (r"Driver 616\.64\+ faults with renodx-dlss5 4\.6/4\.7 - install again \(the tool pins 4\.55\), or try the standalone route\.", "驱动 616.64 及更新版本与 renodx-dlss5 4.6/4.7 存在异常。请重新安装以使用固定的 4.55 版本，或尝试 Standalone 路线。"),
    (r"Driver 616\.64\+ faults with renodx-dlss5 4\.6/4\.7 - install again \(the tool pins 4\.55\)\.", "驱动 616.64 及更新版本与 renodx-dlss5 4.6/4.7 存在异常。请重新安装以使用固定的 4.55 版本。"),
    (r"Not started since the install - run the (.+) once, then check again\.", "安装后尚未运行。请运行一次 {0} 后重新检查。"),
    (r"The (.+) has not been started since the install\.", "安装后尚未启动 {0}。"),
    (r"If you DID start it, it launches something other than (.+)\.", "如果已启动游戏，实际运行的可能不是 {0}。"),
    (r"Inconclusive - open the overlay \((.+)\) and read the status under the Neural Rendering checkbox\.", "日志不足以判断。请按 {0} 打开浮层，查看 Neural Rendering 复选框下的状态。"),
    (r"Add-ons loaded\. Confirm in the (.+) - this route does not log frames\.", "插件已加载。当前路线不记录逐帧日志，请在 {0} 中确认状态。"),
    (r"Loaded, but switched off in the (.+)\.", "插件已加载，但在 {0} 中未开启。"),
    (r"ReShade's (.+) is missing from the folder - reinstall\.", "目录中缺少 ReShade 的 {0}，请重新安装组件。"),
    (r"ReShade's (.+) is gone from the folder\.", "目录中的 ReShade 文件 {0} 已丢失。"),
    (r"The (32|64)-bit ReShade Vulkan layer is not registered - install again\.", "{0} 位 ReShade Vulkan 层未注册，请重新安装组件。"),
    (r"DXVK ran and ReShade did not - install again to rewrite the (32|64)-bit Vulkan layer\.", "DXVK 已运行，ReShade 未运行。请重新安装组件以修复 {0} 位 Vulkan 层。"),
    (r"A ReShade Vulkan layer is registered, but not the (32|64)-bit one this game needs\.", "已注册的 ReShade Vulkan 层与游戏所需的 {0} 位架构不匹配。"),
    (r"The neural feature was refused by NGX \((.+)\)\.", "NGX 拒绝了神经渲染功能，错误码：{0}。"),
    (r"NGX refused the neural feature \((.+)\)\.", "NGX 拒绝了神经渲染功能，错误码：{0}。"),
    (r"ReShade loaded add-on: (.+)", "ReShade 已加载插件：{0}"),
    (r"Add-on missing from the folder: (.+)\.", "目录中缺少插件：{0}。"),
    (r"The '(.+)' add-on did not load\.", "插件 {0} 未加载。"),
    (r"DXVK is gone from the folder: (.+)\.", "目录中缺少 DXVK 文件：{0}。"),
    (r"Written by the install and no longer in the folder: (.+)\.", "本次安装写入的文件已丢失：{0}。"),
    (r"nvngx_dlssnr.dll is missing from (.+)\.", "{0} 中缺少 nvngx_dlssnr.dll。"),
    (r"OptiScaler never saw the game's (.+) calls\.", "OptiScaler 未捕获游戏的 {0} 调用。"),
    (r"The game refused the swapchain OptiScaler wrapped \((.+)\)\.", "游戏拒绝了 OptiScaler 的交换链，错误码：{0}。"),
    (r"DLSS 5 is running inside Remix \(feature (.+)\)\.", "DLSS 5 正在 Remix 中运行，功能：{0}。"),
    (r"The neural pass did not start: (.+)", "神经渲染未启动：{0}"),
    (r"Another DLSS hook shares this folder: (.+)", "目录中还有其他 DLSS 接入组件：{0}"),
    (r"Other ReShade add-ons are loaded: (.+)", "还加载了其他 ReShade 插件：{0}"),
    (r"Creating the DLSS feature crashed \((.+)\)\.", "创建 DLSS 功能时崩溃，错误码：{0}。"),
    (r"The add-on could not hook (.+)\.", "插件无法接入 {0}。"),
    (r"This machine's driver, (.+), is older than DLSS 5 itself\.", "当前驱动 {0} 早于 DLSS 5，需要更新。"),
    (r"Neural pass at (.+), the game presents (.+)\.", "神经渲染分辨率：{0}；游戏输出分辨率：{1}。"),
    (r"Frames are being processed \((\d+) logged, last was frame (\d+)\)\.", "画面正在处理；记录了 {0} 帧，最后一帧编号为 {1}。"),
    (r"Frames are going through the pipeline \((\d+) logged, last was frame (\d+)\)\.", "画面正在通过处理流程；记录了 {0} 帧，最后一帧编号为 {1}。"),
    (r"The pipeline failed at (.+)\.", "处理流程在以下阶段失败：{0}。"),
    (r"Active contract: (.+)", "当前运行配置：{0}"),
    (r"Motion vectors: (.+) is enabled\.", "运动矢量：{0} 已开启。"),
    (r"Motion vectors: (.+) is installed but not switched on\.", "运动矢量：{0} 已安装，但未开启。"),
    (r"Motion vectors: (.+) is not installed\.", "运动矢量：{0} 未安装。"),
    (r"Motion vectors look alive \((.+)% non-zero\)\.", "运动矢量包含有效数据，非零比例为 {0}%。"),
    (r"(.+) frames at (.+) fps, (.+) ms/frame spent on the feed\.", "记录了 {0} 帧，帧率为 {1} FPS；Feeder 每帧耗时 {2} ms。"),
    (r"ReShade failed to (.+): (.+)", "ReShade 操作失败：{0}；对象：{1}"),
    (r"(\d+) other shaders? failed to compile - not used by the feed, ignore\.", "另有 {0} 个着色器编译失败；Feeder 未使用这些着色器，可忽略。"),
    (r"Or the (.+) is not running on Vulkan\.", "也可能是 {0} 没有使用 Vulkan。"),
    (r"Or the (.+) does not render with OpenGL\.", "也可能是 {0} 没有使用 OpenGL。"),
    (r"Or the (.+) ignores (.+)\.", "也可能是 {0} 没有加载 {1}。"),
    (r"The add-on hooked the game's DLSS call \((\d+) entry points?\)\.", "插件已接入游戏的 DLSS 调用，共 {0} 个入口。"),
    (r"The add-on's log stops at a device re-creation \((.+)\)\.", "插件日志在重建图形设备时停止：{0}。"),
    (r"DLSS 5 add-on (.+), classic engine", "DLSS 5 插件版本：{0}，经典引擎"),
    (r"The game was presenting a few pixels short of its display size \((.+) against (.+)\)\.", "游戏输出尺寸略小于显示尺寸：{0}，显示尺寸为 {1}。"),
    (r"The game window was minimized while the feed was running \(rebuilt at (.+)\)\.", "Feeder 运行时游戏窗口被最小化，重建尺寸为 {0}。"),
    (r"Rebuilt at (\d+) different resolutions \((.+)\)\.", "曾按 {0} 种分辨率重建：{1}。"),
    (r"The game crashed \((.+)\), and the feed recorded it while (.+)\.", "游戏崩溃，错误码 {0}；Feeder 记录的当时状态：{1}。"),
    (r"The feed recorded a crash \((.+)\) while (.+)\.", "Feeder 记录到崩溃，错误码 {0}；当时状态：{1}。"),
    (r"The crash \((.+)\) is inside the Direct3D 12 / NGX runtime \((.+)\), reached through (.+)\.", "崩溃错误码 {0}，堆栈位于 Direct3D 12 / NGX 运行库（{1}），调用经过 {2}。"),
    (r"(\d+) of (\d+) frames went through untouched\.", "{1} 帧中有 {0} 帧未经处理直接通过。"),
    (r"The add-on logged failures \((\d+) exposure, (\d+) guides\)\.", "插件记录了失败：曝光 {0} 次，引导数据 {1} 次。"),
    (r"Neural rendering is running \((\d+) heartbeats, (.+)\)\.", "神经渲染正在运行，记录了 {0} 次心跳；{1}。"),
    (r"Neural rendering is running \((\d+) heartbeats\)\.", "神经渲染正在运行，记录了 {0} 次心跳。"),
    (r"The add-on is in the frame but produces nothing \((\d+) heartbeats, no valid result\)\.", "插件已接入画面，但未产生有效结果；记录了 {0} 次心跳。"),
    (r"(\d+) builds of the same add-on are loaded: (.+)\.", "同时加载了同一插件的 {0} 个版本：{1}。"),
    (r"NGX refused the neural feature \((.+)\); the add-on ran its own snippet instead\.", "NGX 拒绝了神经渲染功能，错误码 {0}；插件改用了自带模块。"),
    (r"Motion vectors: (.+) is (.+)\.", "运动矢量：{0}；来源报告的状态：{1}。"),
]
PATTERNS = [(re.compile(source), target) for source, target in _PATTERNS]

# Brief next steps for actionable findings. These supplement, rather than
# replace, the complete upstream evidence available beside each finding.
NEXT_STEPS = {
    "The install did not finish.": ("查看任务日志中的失败原因后重试安装；已下载的有效文件会复用。", "Review the failed step in Activity, then retry installation; valid downloads are reused."),
    "The uninstall did not finish.": ("关闭游戏后再次卸载；如果仍失败，请检查文件权限。", "Close the game and uninstall again; check file permissions if it fails."),
    "The bridge replaced the settings this install wrote.": ("请重新安装 Bridge 路线以恢复所需配置。", "Reinstall the Bridge route to restore the required configuration."),
    "ReShade is not giving the feed a depth buffer.": ("打开 ReShade 的 Add-ons 页面，检查是否选中了深度缓冲区。若匹配异常，可尝试关闭 Use aspect ratio heuristics。", "In ReShade's Add-ons tab, check the selected depth buffer. If matching fails, try turning off Use aspect ratio heuristics."),
    "The helper started but never connected.": ("展开详细说明，检查辅助进程与游戏的连接记录。", "Expand the details and check the connection records for the helper and game."),
    "The game's own d3dcompiler_47.dll is too old for the neural pass.": ("重新安装组件会处理旧编译器；关闭游戏后操作。", "Close the game and reinstall components to handle the older compiler."),
    "The log predates the current install.": ("运行一次游戏后重新检查。", "Run the game once, then check again."),
    "ReShade.log is older than the install.": ("运行一次游戏后重新检查。", "Run the game once, then check again."),
    "Neural rendering is switched off.": ("在插件浮层中开启神经渲染后，再运行检查。", "Enable neural rendering in the add-on overlay, then check again."),
}


def translate(text, chinese=True):
    """Return None for an untranslated message; callers must show its source."""
    if not chinese:
        return text
    if text in MESSAGES:
        return MESSAGES[text]
    for pattern, target in PATTERNS:
        match = pattern.fullmatch(text)
        if match:
            return target.format(*match.groups())
    return None
