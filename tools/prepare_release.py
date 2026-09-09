"""Produce reviewable release assets with pinned source and license materials."""
import hashlib
from importlib.metadata import distribution
import json
import os
from pathlib import Path, PurePosixPath
import platform
import shutil
import ssl
import subprocess
import sys
import tarfile
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from frontend.about import VERSION


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def fetch(source, cache):
    target = cache / f"{source['name']}-{source['version']}.tar.gz"
    if target.exists() and sha256(target) == source["sha256"]:
        return target
    temporary = target.with_suffix(".download")
    request = urllib.request.Request(source["url"], headers={"User-Agent": "JustDLSS5-release-builder"})
    with urllib.request.urlopen(request, timeout=90) as response, temporary.open("wb") as output:
        total = 0
        while chunk := response.read(1024 * 1024):
            total += len(chunk)
            if total > 200 * 1024 * 1024:
                raise ValueError("Source archive exceeds 200 MiB")
            output.write(chunk)
    if sha256(temporary) != source["sha256"]:
        raise ValueError(f"Source checksum mismatch: {source['name']}")
    temporary.replace(target)
    return target


def license_path(name):
    path = PurePosixPath(name)
    if path.is_absolute() or any(part in ("..", "") or ":" in part or "\\" in part for part in path.parts):
        raise ValueError("Unsafe source archive path")
    return Path(*path.parts[1:])


def collect_notices(archive, destination):
    count = 0
    with tarfile.open(archive) as source:
        for member in source:
            if not member.isfile():
                continue
            relative = license_path(member.name)
            name = relative.name.lower()
            is_notice = any(word in name for word in ("license", "licence", "copying", "copyright", "notice"))
            is_notice |= any(part.lower() in ("licenses", "licences") for part in relative.parts)
            is_notice |= name == "qt_attribution.json" or ("3rdparty" in relative.parts and name.startswith("readme"))
            if not is_notice:
                continue
            if member.size > 4 * 1024 * 1024:
                raise ValueError("Unexpectedly large license file")
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.extractfile(member).read())
            count += 1
    if not count:
        raise ValueError(f"No license materials found in {archive.name}")
    return count


def make_zip(folder, output):
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in sorted(folder.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(folder.parent).as_posix())


def main():
    if platform.python_version() not in ("3.12.10", "3.12.14"):
        raise SystemExit("Missing pinned Python source materials")
    for name in ("PySide6-Essentials", "shiboken6"):
        if distribution(name).version != "6.11.2":
            raise SystemExit(f"Update the pinned source materials for {name}")
    app = Path(os.environ.get("STUDIO_DIST_DIR", ROOT / "dist" / ("v" + VERSION))) / "JustDLSS5"
    if not (app / "JustDLSS5.exe").is_file():
        raise SystemExit("Build and smoke-test the desktop first")
    cache = ROOT / "build/release-sources"
    cache.mkdir(parents=True, exist_ok=True)
    output = ROOT / "dist" / ("release-v" + VERSION)
    output.mkdir(parents=True, exist_ok=True)
    legal = app / "LICENSES"
    legal.mkdir(exist_ok=True)
    sources = json.loads((ROOT / "tools/release-sources.json").read_text(encoding="utf8"))
    openssl_version = ssl.OPENSSL_VERSION.split()[1]
    if not any(s["name"] == "openssl" and s["version"] == openssl_version for s in sources):
        raise SystemExit(f"Missing corresponding OpenSSL source: {openssl_version}")
    sources = [s for s in sources if (s["name"] != "openssl" or s["version"] == openssl_version)
               and (s["name"] != "cpython" or s["version"] == platform.python_version())]
    archives = []
    for source in sources:
        archive = fetch(source, cache)
        count = collect_notices(archive, legal / source["name"])
        archives.append(archive)
        print(f"{source['name']}: {count} license/attribution files", flush=True)
    for name in ("LGPL-3.0-only.txt", "GPL-3.0-only.txt"):
        if not (legal / "qtbase/LICENSES" / name).is_file():
            raise SystemExit(f"Required Qt license missing: {name}")
    for name in ("PySide6-Essentials", "shiboken6", "pyinstaller", "certifi"):
        package = distribution(name)
        for file in package.files or ():
            if "licenses" in file.parts:
                target = legal / name / file.name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(package.locate_file(file), target)
    shutil.copyfile(Path(sys.base_prefix) / "LICENSE.txt", legal / "Python-distribution-LICENSE.txt")
    shutil.copytree(ROOT / "licenses", legal / "supplemental", dirs_exist_ok=True)
    for source, target in (("LICENSE", "LICENSE.txt"),
                           ("docs/THIRD-PARTY-NOTICES.md", "THIRD-PARTY-NOTICES.md"),
                           ("docs/TESTING-PREVIEW.zh-CN.md", "START-HERE.zh-CN.md"),
                           ("tools/release-sources.json", "DEPENDENCY-SOURCES.json")):
        shutil.copyfile(ROOT / source, app / target)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    manifest = {"version": VERSION, "commit": commit, "python": platform.python_version(),
                "openssl": ssl.OPENSSL_VERSION, "pyside": distribution("PySide6-Essentials").version,
                "pyinstaller": distribution("pyinstaller").version, "certifi": distribution("certifi").version,
                "workflow": os.environ.get("GITHUB_RUN_ID"),
                "engine": json.loads((ROOT / "backend-version.json").read_text(encoding="utf8")),
                "files": {p.relative_to(app).as_posix(): sha256(p) for p in sorted(app.rglob("*"))
                          if p.is_file() and p.name != "BUILD-INFO.json"}}
    # The upstream lock can contain a local backup path; it is not release metadata.
    manifest["engine"] = {k: v for k, v in manifest["engine"].items() if k in ("repository", "repo", "ref", "sha", "commit", "version")}
    (app / "BUILD-INFO.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf8")
    binary = output / f"JustDLSS5-v{VERSION}-windows-x64.zip"
    make_zip(app, binary)
    source_zip = output / f"JustDLSS5-v{VERSION}-source-materials.zip"
    own_source = cache / f"JustDLSS5-{commit}.tar"
    subprocess.run(["git", "archive", "--format=tar", "--output", str(own_source), commit], cwd=ROOT, check=True)
    with zipfile.ZipFile(source_zip, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in [*archives, own_source, ROOT / "tools/release-sources.json", ROOT / "docs/THIRD-PARTY-NOTICES.md"]:
            archive.write(path, path.name)
    (output / "SHA256SUMS.txt").write_text("".join(f"{sha256(p)}  {p.name}\n" for p in (binary, source_zip)), encoding="ascii")
    shutil.copyfile(app / "BUILD-INFO.json", output / "BUILD-INFO.json")
    print(f"Release candidate prepared in {output}")


if __name__ == "__main__":
    main()
