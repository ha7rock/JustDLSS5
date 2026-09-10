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


if __name__ == "__main__":
    unittest.main()
