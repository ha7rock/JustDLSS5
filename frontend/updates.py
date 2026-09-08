"""Read-only product release checks. Never invoke the upstream self-updater."""
from dataclasses import dataclass
import json
import re
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from .about import REPOSITORY, VERSION

API = "https://api.github.com/repos/ha7rock/JustDLSS5/releases?per_page=30"


def check_due(last_checked, now):
    try:
        last = float(last_checked or 0)
        return not (0 <= now - last < 86400)
    except (TypeError, ValueError):
        return True


@dataclass(frozen=True)
class Result:
    status: str
    version: str = ""
    url: str = ""


def version_key(value):
    match = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)(?:-(alpha|beta|rc)\.(\d+))?", value)
    if not match:
        return None
    major, minor, patch, stage, number = match.groups()
    return (int(major), int(minor), int(patch), {"alpha": 0, "beta": 1, "rc": 2, None: 3}[stage], int(number or 0))


def select_release(releases, current=VERSION, preview=False):
    installed = version_key(current)
    if installed is None or not isinstance(releases, list):
        return Result("unavailable")
    candidates = []
    for release in releases:
        if not isinstance(release, dict) or release.get("draft", True):
            continue
        tag = release.get("tag_name", "")
        key = version_key(tag) if isinstance(tag, str) else None
        if key is None or (not preview and (release.get("prerelease", True) or key[3] != 3)):
            continue
        candidates.append((key, tag))
    if not candidates:
        return Result("no_release")
    key, tag = max(candidates)
    if key <= installed:
        return Result("current")
    return Result("available", tag, REPOSITORY + "/releases/tag/" + quote(tag, safe=""))


def check(preview=False):
    request = Request(API, headers={"Accept": "application/vnd.github+json", "User-Agent": "JustDLSS5/" + VERSION})
    try:
        with urlopen(request, timeout=10) as response:
            payload = response.read(1024 * 1024 + 1)
        if len(payload) > 1024 * 1024:
            return Result("unavailable")
        return select_release(json.loads(payload), preview=preview)
    except HTTPError as error:
        return Result("restricted" if error.code in (401, 403, 404, 429) else "unavailable")
    except (URLError, OSError, ValueError):
        return Result("unavailable")
