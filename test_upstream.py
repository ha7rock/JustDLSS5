"""Offline checks for upstream behavior and the desktop library adapter."""
import ssl
import struct
import zipfile
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core import games, library, feedcfg, optiscaler, installer, net, pe, video, diagnose
from frontend.service import BackendService, LibraryEntry


class UpstreamTests(unittest.TestCase):
    def test_diagnostic_catalog_covers_pinned_static_titles_and_verdicts(self):
        import ast
        from frontend.diagnostic_text import translate
        tree = ast.parse(Path(diagnose.__file__).read_text(encoding="utf8"))
        messages = set()
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "add" and len(node.args) > 1
                    and isinstance(node.args[1], ast.Constant)):
                messages.add(node.args[1].value)
            if (isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant)
                    and any(isinstance(target, ast.Attribute) and target.attr == "verdict" for target in node.targets)):
                messages.add(node.value.value)
        self.assertGreater(len(messages), 100)
        self.assertEqual([message for message in sorted(messages) if translate(message) is None], [])

    def test_diagnostic_translation_preserves_values_and_unknown_messages(self):
        from frontend.diagnostic_text import translate
        path = r"C:\游戏\info check\nvngx_dlssnr.dll"
        text = f"Add-on missing from the folder: {path}."
        self.assertIn(path, translate(text))
        self.assertEqual(translate(text, False), text)
        self.assertIn("0xBAD", translate("The neural feature was refused by NGX (0xBAD)."))
        self.assertIsNone(translate("New upstream warning: " + text))
        self.assertIsNone(translate(path))

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.folder = self.root / "game"
        self.folder.mkdir()
        self.exe = self.folder / "game.exe"
        self.exe.write_bytes(b"fixture")
        self.game = games.Game(name="Fixture", folder=self.folder, exe=self.exe, api="DX11", bitness=64)
        for mock in (patch.object(library, "FILE", self.root / "library.json"),
                     patch.object(games, "api_override", return_value=""),
                     patch("urllib.request.urlopen", side_effect=AssertionError("Unexpected network"))):
            mock.start()
            self.addCleanup(mock.stop)
        self.service = BackendService()
        self.service._gpu = ("Fixture GPU", 86)
        decorate = patch.object(self.service, "decorate", side_effect=lambda game: LibraryEntry(game, bool(game.installed)))
        decorate.start()
        self.addCleanup(decorate.stop)

    def save(self):
        library.save([self.game], {}, self.service._cache_version(), 86)

    def test_unchanged_cache_avoids_full_scan_and_enrichment(self):
        self.save()
        with patch.object(games, "scan_all", side_effect=AssertionError("Unexpected scan")), \
             patch.object(games, "enrich", side_effect=AssertionError("Unchanged game re-read")):
            entries = self.service.load_library(lambda *args: None)
        self.assertEqual(entries[0].game.exe, self.exe)

    def test_changed_executable_is_rechecked_and_keeps_selection(self):
        self.save()
        self.exe.write_bytes(b"updated executable fixture")
        with patch.object(games, "enrich") as enrich:
            self.service.load_library(lambda *args: None)
        enrich.assert_called_once()
        self.assertTrue(enrich.call_args.kwargs["chosen"])

    def test_deleted_executable_does_not_return_from_cache(self):
        self.save()
        self.exe.unlink()
        with patch.object(games, "enrich"):
            self.assertEqual(self.service.load_library(lambda *args: None), [])

    def test_cache_version_gpu_and_corruption_invalidate(self):
        self.save()
        self.assertIsNone(library.load("old", 86))
        self.assertIsNone(library.load(self.service._cache_version(), 89))
        library.FILE.write_text("broken", encoding="utf8")
        self.assertEqual(self.service.load_library(lambda *args: None), [])

    def test_manual_api_overrides_cache(self):
        self.save()
        with patch.object(games, "api_override", return_value="DX12"):
            self.assertEqual(self.service.load_library(lambda *args: None)[0].game.api, "DX12")

    def test_manual_game_is_remembered(self):
        with patch.object(games, "manual", return_value=self.game):
            self.service.manual(self.exe)
        self.assertEqual(self.service.load_library(lambda *args: None)[0].game.exe, self.exe)

    def test_decimal_comma_config(self):
        (self.folder / "dlss5-feed.cfg").write_text("mv_scale_x=1,000\nmv_scale_y=0,500\n")
        feedcfg.write(self.folder)
        self.assertEqual(float(feedcfg.read(self.folder / "dlss5-feed.cfg")["mv_scale_y"]), .5)

    def test_certificates_and_tls_verification_are_enabled(self):
        import certifi
        self.assertTrue(Path(certifi.where()).is_file())
        with patch.object(net, "_SSL", None):
            context = net.ssl_context()
        self.assertTrue(context.check_hostname)
        self.assertEqual(context.verify_mode, ssl.CERT_REQUIRED)
        self.assertGreater(len(context.get_ca_certs()), 0)

    def test_new_build_survives_profile_roundtrip(self):
        from core import profiles, dlss
        with patch.object(profiles, "DIR", self.root / "profiles"):
            options = installer.Options(path=dlss.OPTI, opti_build=optiscaler.PRESR)
            profiles.save("fixture", options)
            loaded = profiles.load("fixture")
        self.assertEqual(loaded.opti_build, optiscaler.PRESR)

    def test_delay_imports_read_both_pe_architectures(self):
        for magic, optional_size, directory_offset in ((0x10B, 224, 96), (0x20B, 240, 112)):
            data = bytearray(0x600)
            data[:2] = b"MZ"
            struct.pack_into("<I", data, 0x3C, 0x80)
            data[0x80:0x84] = b"PE\0\0"
            struct.pack_into("<H", data, 0x86, 1)
            struct.pack_into("<H", data, 0x94, optional_size)
            optional = 0x98
            struct.pack_into("<H", data, optional, magic)
            struct.pack_into("<I", data, optional + directory_offset - 4, 16)
            struct.pack_into("<II", data, optional + directory_offset + 13 * 8, 0x1000, 64)
            struct.pack_into("<IIII", data, optional + optional_size + 8, 0x400, 0x1000, 0x400, 0x200)
            struct.pack_into("<II", data, 0x200, 1, 0x1100)
            data[0x300:0x30A] = b"d3d11.dll\0"
            self.exe.write_bytes(data)
            self.assertEqual(pe.pe_imports(self.exe), [])
            self.assertEqual(pe.pe_imports(self.exe, delay=True), ["d3d11.dll"])

    def test_selected_fork_preview_stays_offline(self):
        def cached(url):
            name = "presr-fixture" if url == optiscaler.PRESR_API else "other"
            return [{"tag_name": name, "assets": [{"name": name + ".zip", "browser_download_url": "https://example.invalid/fixture.zip"}]}]
        with patch.object(optiscaler.sources, "cached_json", side_effect=cached):
            self.assertIn("presr-fixture", optiscaler.archive_name(optiscaler.PRESR))

    def test_ffmpeg_api_failure_uses_direct_download(self):
        archive = self.root / "fixture.zip"
        with zipfile.ZipFile(archive, "w") as output:
            output.writestr("fixture/bin/ffmpeg.exe", b"fixture")
            output.writestr("fixture/bin/ffprobe.exe", b"fixture")
        with patch.object(video.sources, "_json", side_effect=OSError("offline")), \
             patch.object(video.net, "download", return_value=archive) as download:
            video.ensure_ffmpeg(self.folder)
        self.assertEqual(download.call_args.args[0], video.FFMPEG_DIRECT)

    def test_diagnosis_uses_latest_reshade_session(self):
        marker = "Initializing crosire's ReShade"
        self.assertEqual(diagnose._last_session(marker + " old\n" + marker + " current"), marker + " current")


    def test_vulkan_32_and_64_manifests_have_distinct_names(self):
        import json
        from core import vulkan
        archive = self.root / "reshade.zip"
        with zipfile.ZipFile(archive, "w") as output:
            for dll, manifest in ((vulkan.DLL, vulkan.MANIFEST), (vulkan.DLL32, vulkan.MANIFEST32)):
                output.writestr(dll, b"fixture")
                output.writestr(manifest, json.dumps({"layer": {"name": vulkan.LAYER_NAME}}))
        for dll, manifest in ((vulkan.DLL, vulkan.MANIFEST), (vulkan.DLL32, vulkan.MANIFEST32)):
            vulkan._place(archive, self.folder, dll, manifest)
        self.assertNotEqual(vulkan.layer_name(self.folder / vulkan.MANIFEST),
                            vulkan.layer_name(self.folder / vulkan.MANIFEST32))

    def test_archive_paths_cannot_escape_target(self):
        for path in ("../escape.dll", "..\\escape.dll", str(self.root / "outside.dll")):
            with self.subTest(path=path), self.assertRaises(net.OutsideError):
                net.inside(self.folder, path)
        self.assertEqual(net.inside(self.folder, "bin/runtime.dll"), (self.folder / "bin/runtime.dll").resolve())

    def test_analysis_proposes_without_writing_game_config(self):
        from types import SimpleNamespace
        from core import prefs, dlss, wincrash
        from frontend.session import analyse
        config = self.folder / "dlss5-feed.cfg"
        config.write_text("work_resolution=100\n")
        (self.folder / diagnose.FEED_LOG).write_text("3600 frames: feed CPU 1.0 ms/frame 47 fps")
        report = SimpleNamespace(verdict="Working.", ran=True, findings=[])
        with patch.object(diagnose, "analyse", return_value=report), \
             patch.object(diagnose, "_manifest", return_value={"path": dlss.FEEDER}), \
             patch.object(diagnose, "_installed_at", return_value=1), \
             patch.object(wincrash, "last_crash", return_value=None), \
             patch.object(prefs, "FILE", self.root / "prefs.json"):
            result = analyse(LibraryEntry(self.game, True), 60)
        self.assertGreater(result.resolution, 0)
        self.assertLess(result.resolution, 100)
        self.assertEqual(config.read_text(), "work_resolution=100\n")

    def test_tuning_applies_only_to_matching_install_and_settings(self):
        from core import dlss
        from frontend.session import SessionResult, apply
        config = self.folder / "dlss5-feed.cfg"
        config.write_text("work_resolution=100\n")
        result = SessionResult("", str(self.folder), dlss.FEEDER, 75, 100)
        item = LibraryEntry(self.game, True)
        with patch.object(installer, "options_from_manifest", return_value=installer.Options(path=dlss.OPTI)):
            with self.assertRaises(ValueError):
                apply(item, result)
        with patch.object(installer, "options_from_manifest", return_value=installer.Options(path=dlss.FEEDER)):
            self.assertEqual(apply(item, result), 75)
            with self.assertRaises(ValueError):
                apply(item, result)
        self.assertEqual(float(feedcfg.read(config)["work_resolution"]), 75)

    def test_silent_opti_write_failure_is_reported(self):
        from core import dlss
        from frontend.session import SessionResult, apply
        (self.folder / "OptiScaler.ini").write_text("[DlssNr]\nWorkingScale=1.0\n")
        result = SessionResult("", str(self.folder), dlss.OPTI, 75, 100)
        with patch.object(installer, "options_from_manifest", return_value=installer.Options(path=dlss.OPTI)), \
             patch.object(optiscaler, "enable_nr"):
            with self.assertRaises(OSError):
                apply(LibraryEntry(self.game, True), result)

    def test_old_crash_cannot_override_latest_session(self):
        from datetime import datetime, timezone, timedelta
        from core import wincrash
        from frontend.session import current_crash
        (self.folder / "ReShade.log").write_text("new session")
        old = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        crash = wincrash.Crash(old, "game.exe", "game.exe", "0xc0000005", "Application Error")
        self.assertFalse(current_crash(crash, self.folder))
        crash.when = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        self.assertTrue(current_crash(crash, self.folder))

    def test_overlay_key_preserves_other_settings(self):
        from core import reshade_ini
        config = self.folder / "ReShade.ini"
        config.write_text("[INPUT]\nKeyOverlay=36,0,0,0\nKeyEffects=117,0,0,0\n")
        reshade_ini.set_overlay_key(self.folder, 0x7A)
        text = config.read_text()
        self.assertIn("122,0,0,0", text)
        self.assertIn("117,0,0,0", text)


    def test_bridge_keeps_configuration_across_runtime_versions(self):
        file = feedcfg.write_bridge(self.folder, feedcfg.bridge_defaults(False))
        self.assertEqual(file.read_text().splitlines()[0], "# dlss5-bridge keep")
        self.assertEqual(feedcfg.read(file)["synth_after"], "3")
        feedcfg.write_bridge(self.folder, feedcfg.bridge_defaults(True))
        self.assertEqual(feedcfg.read(file)["synth_after"], "0")

    def test_opti_logging_and_fork_update_notice(self):
        file = self.folder / "OptiScaler.ini"
        file.write_text("[Log]\nLogToFile=auto\nLogLevel=5\n[Custom]\nKeep=1\n")
        optiscaler.enable_nr(self.folder, settings={"WorkingScale": .75})
        text = file.read_text()
        self.assertEqual(optiscaler._ini_get(text, "Log", "LogToFile"), "true")
        self.assertEqual(optiscaler._ini_get(text, "Log", "LogLevel"), "5")
        self.assertEqual(optiscaler._ini_get(text, "Hotfix", "CheckForUpdate"), "false")
        self.assertIn("Keep=1", text)

    def test_cached_duplicate_retains_manual_api_entry(self):
        from dataclasses import replace
        from core import log
        other = self.root / "other"
        other.mkdir()
        preferred = replace(self.game, folder=other, source="Manual")
        library.save([self.game, preferred], {}, self.service._cache_version(), 86)
        with patch.object(games, "api_override", side_effect=lambda folder: "DX12" if folder == other else ""), \
             patch.object(log, "write"):
            entries = self.service.load_library(lambda *args: None)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].game.folder, other)
        self.assertEqual(entries[0].game.api, "DX12")

    def test_full_executable_wins_over_same_game_trial(self):
        trial = self.folder / "gameTrial.exe"
        trial.write_bytes(b"fixture")
        with patch.object(pe, "_walk_exes", return_value=[trial, self.exe]), \
             patch.object(pe, "_score", return_value=1000):
            self.assertEqual(pe.find_game_exes(self.folder)[0], self.exe)
            self.assertIn(trial, pe.find_game_exes(self.folder))

    def test_invalid_cached_archive_is_replaced(self):
        import io
        contents = io.BytesIO()
        with zipfile.ZipFile(contents, "w") as archive:
            archive.writestr("fixture.txt", "fixture")
        response = io.BytesIO(contents.getvalue())
        response.status = 200
        response.headers = {"Content-Length": str(len(contents.getvalue()))}
        cached = self.root / "download.zip"
        cached.write_bytes(b"<html>proxy error</html>")
        with patch.object(net, "CACHE", self.root), \
             patch("urllib.request.urlopen", return_value=response) as request:
            result = net.download("https://example.invalid/file.zip", cached.name)
        request.assert_called_once()
        self.assertTrue(zipfile.is_zipfile(result))

    def test_crash_library_does_not_choose_graphics_api(self):
        dll = self.folder / "GFSDK_Aftermath_Lib.x64.dll"
        dll.write_bytes(b"fixture")
        with patch.object(pe, "_engine_default", return_value=None), \
             patch.object(pe, "_names_in", return_value=set()), \
             patch.object(pe, "_ours_in", return_value=set()), \
             patch.object(pe, "pe_imports", return_value=["d3d12.dll"]) as imports:
            pe._runtime_graphics(self.exe)
        self.assertNotIn(dll, [call.args[0] for call in imports.call_args_list])

    def test_mfg_wrong_archive_shape_is_rejected_before_writes(self):
        from core import mfg
        archive = self.root / "changed.zip"
        with zipfile.ZipFile(archive, "w") as output:
            output.writestr("unexpected.txt", "fixture")
        before = set(self.folder.iterdir())
        with patch.object(mfg, "loader_name", return_value="version.dll"), \
             patch.object(mfg, "resolve", return_value=("fixture", "https://example.invalid/mfg.zip")), \
             patch.object(mfg, "resolve_loader", return_value=("fixture", "https://example.invalid/loader.zip")), \
             patch.object(net, "download", return_value=archive):
            with self.assertRaises(mfg.ShapeChanged):
                mfg.install(self.folder, self.exe)
        self.assertEqual(set(self.folder.iterdir()), before)


if __name__ == "__main__":
    unittest.main()
