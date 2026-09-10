"""Build a user-reviewed GitHub issue URL without logs or local paths."""
import platform
from urllib.parse import urlencode

from .about import NAME, VERSION, REPOSITORY


def report_fields(engine_version, entry=None, inspection=None, route=""):
    fields = {"versions": f"{NAME} {VERSION}\nCore {engine_version}",
              "platform": f"{platform.system()} {platform.release()} ({platform.version()})"}
    if entry:
        game = entry.game
        fields["game"] = str(game.name)[:120]
        fields["store"] = str(game.source)[:80]
        fields["configuration"] = f"API: {game.api}\nArchitecture: {game.bitness}\nRoute: {route}\nAnti-cheat: {entry.anticheat or 'Not detected / 未检测到'}"
    if inspection and inspection.gpu_name:
        fields["hardware"] = str(inspection.gpu_name)[:120] + "\nDriver / 驱动版本：" + str(getattr(inspection, "driver", "") or "Unknown / 不清楚")
    return fields


def issue_url(fields):
    allowed = {"versions", "platform", "game", "store", "configuration", "hardware"}
    values = {key: str(value)[:500] for key, value in fields.items() if key in allowed}
    return REPOSITORY + "/issues/new?" + urlencode({"template": "bug-report.yml", **values})
