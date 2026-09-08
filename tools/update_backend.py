"""Stage an upstream ref, validate it, then optionally replace only core/.

Usage: python tools/update_backend.py v1.6.1 [--apply]
The default is a dry run. Close the app before using --apply.
"""
import argparse
import io
import json
import shutil
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = "https://github.com/Kizzuwatnaa/DLSS5-Autopilot.git"


def run(*args, cwd=ROOT):
    return subprocess.check_output(args, cwd=cwd)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ref", help="Upstream tag or commit to validate")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.ref.startswith("-"):
        parser.error("ref must be a tag, branch or commit")
    with tempfile.TemporaryDirectory(prefix="dlss5-backend-") as work:
        checkout = Path(work) / "upstream"
        run("git", "clone", "--bare", "--filter=blob:none", UPSTREAM, str(checkout))
        commit = run("git", "rev-parse", "--verify", args.ref + "^{commit}", cwd=checkout).decode().strip()
        archive = run("git", "archive", commit, "core", cwd=checkout)
        candidate = Path(work) / "candidate"
        candidate.mkdir()
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            for member in tar.getmembers():
                target = (candidate / member.name).resolve()
                if not target.is_relative_to(candidate.resolve()) or member.issym() or member.islnk():
                    raise RuntimeError("Unsafe archive entry: " + member.name)
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                elif member.isfile():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with tar.extractfile(member) as source, target.open("wb") as dest:
                        shutil.copyfileobj(source, dest)
        shutil.copytree(ROOT / "frontend", candidate / "frontend", ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(ROOT / "tools", candidate / "tools", ignore=shutil.ignore_patterns("__pycache__"))
        for filename in ("test_ui.py", "test_cli.py", "test_product.py", "test_reshade_ini.py",
                         "autopilot_desktop.py", "dlss5_autopilot.py"):
            shutil.copy2(ROOT / filename, candidate / filename)
        for script in ("tools/check_backend.py", "test_ui.py", "test_cli.py", "test_product.py", "test_reshade_ini.py"):
            subprocess.run([sys.executable, script], cwd=candidate, check=True)
        print("Validated backend commit:", commit)
        if not args.apply:
            print("Dry run complete; no project files changed. Add --apply to install this backend.")
            return
        # Same-volume rename keeps rollback possible even if replacement fails.
        backups = ROOT / "backend-backups"
        backups.mkdir(exist_ok=True)
        (backups / ".gitignore").write_text("*\n", encoding="utf8")
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup = backups / stamp
        prepared = backups / (stamp + "-incoming")
        shutil.copytree(candidate / "core", prepared)
        (ROOT / "core").rename(backup)
        try:
            prepared.rename(ROOT / "core")
        except BaseException:
            backup.rename(ROOT / "core")
            raise
        (ROOT / "backend-version.json").write_text(json.dumps(
            {"repository": UPSTREAM, "commit": commit, "ref": args.ref,
             "backup": str(backup.relative_to(ROOT))}, indent=2) + "\n", encoding="utf8")
        print("Backend updated. Frontend unchanged. Backup:", backup)
        print("Rebuild the desktop exe with build-desktop.bat to include the new backend.")


if __name__ == "__main__":
    main()
