"""Independent frontend entry point; the upstream CLI remains available."""
import argparse
import sys


def main():
    if len(sys.argv) > 1:
        from dlss5_autopilot import main as upstream_cli, _console
        from frontend.about import NAME, VERSION
        _console()
        parser = argparse.ArgumentParser(prog=NAME, description="游戏画面组件管理 / Game graphics component manager")
        parser.add_argument("target", nargs="?", help="游戏目录或 EXE / Game folder or executable")
        parser.add_argument("--version", action="version", version=f"{NAME} {VERSION}")
        action = parser.add_mutually_exclusive_group()
        action.add_argument("--check", action="store_true")
        action.add_argument("--remove", action="store_true")
        parser.add_argument("--route", choices=("native", "upstream", "optiscaler", "renodx", "bridge", "feeder", "standalone", "remix"))
        dxvk = parser.add_mutually_exclusive_group()
        dxvk.add_argument("--dxvk", action="store_true")
        dxvk.add_argument("--no-dxvk", action="store_true")
        parser.add_argument("--remix-swap", action="store_true")
        parser.add_argument("--video", action="store_true")
        args = parser.parse_args()
        if not args.target and not args.video:
            parser.error("请指定游戏目录 / A game target is required")
        return upstream_cli()
    from frontend.desktop import run
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
