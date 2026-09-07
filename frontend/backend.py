"""The only business-module import boundary for the desktop frontend.

Upstream owns core/. Compatibility shims belong here, never in core/ or in
individual widgets. Contract validation lives in tools/check_backend.py.
"""
from core import (anticheat, compare, components, diagnose, dlss, dxvk, feedcfg,
                  games, gpu, installer, log, mfg, net, optiscaler, prefs, profiles,
                  reengine, remixdl, remixlist, reshade_ini, selfupdate, sources,
                  update, video)
