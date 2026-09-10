"""Offline regression tests for the Qt desktop and its backend boundary."""
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch, PropertyMock

from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QMouseEvent, QFont
from PySide6.QtWidgets import QApplication, QDialog
from PySide6.QtTest import QTest

from core import games, dlss, installer, prefs, profiles
from frontend.desktop import MainWindow
from frontend.service import BackendService, LibraryEntry, Inspection


def entry(name="测试游戏", installed=False):
    folder = Path("C:/UI-test-fixtures") / name
    game = games.Game(name=name, folder=folder, exe=folder / "game.exe",
                      api="DX12", bitness=64, source="Steam")
    return LibraryEntry(game, installed)


class FakeService:
    def __init__(self):
        self.entries = [entry("Cyberpunk 2077"), entry("Control", True), entry("Portal with RTX")]
        self.installs = []
        self.threads = []
        self.delays = {}

    def hardware(self):
        return "Test GPU", 120

    def scan(self, emit):
        self.threads.append(threading.get_ident())
        emit("log", "scan fixture")
        return self.entries

    def inspect(self, item):
        self.threads.append(threading.get_ident())
        time.sleep(self.delays.get(item.game.name, 0))
        support = dlss.Support(native_dlss=True, recommended=dlss.OPTI,
                               options=[dlss.OPTI, dlss.FEEDER], reason="fixture")
        return Inspection(item, support, {dlss.OPTI: (True, "supported"), dlss.FEEDER: (True, "supported")},
                          installer.Options(path=dlss.OPTI, native_dlss=True), "Test GPU", "stable", "fixture")

    def install(self, item, options, emit):
        self.threads.append(threading.get_ident())
        self.installs.append((item, options))
        emit("progress", (50, "fixture progress"))
        return installer.Report(written=["fixture.dll"])


class DesktopTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.app.setStyle("Fusion")
        cls.app.setFont(QFont("Microsoft YaHei UI", 10))

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.patch = patch.object(prefs, "FILE", Path(self.temp.name) / "prefs.json")
        self.patch.start()
        self.service = FakeService()
        self.window = MainWindow(service=self.service, background=False)
        self.window.show_text = lambda title, text: None
        self.window.show()
        self.app.processEvents()

    def drain(self, timeout=3):
        deadline = time.monotonic() + timeout
        while self.window.jobs.active and time.monotonic() < deadline:
            QTest.qWait(20)
        self.app.processEvents()
        self.assertFalse(self.window.jobs.active, "background jobs did not finish")

    def tearDown(self):
        self.drain()
        self.window.close()
        self.app.processEvents()
        self.patch.stop()
        self.temp.cleanup()

    def select_game(self, index=0):
        self.window._scanned(self.service.entries)
        self.window.table.selectRow(index)
        self.drain()

    def test_starts_in_library_without_scan_or_io(self):
        self.assertEqual(self.window.pages.currentIndex(), 0)
        self.assertEqual(self.window.model.rowCount(), 0)
        self.assertFalse(self.service.threads)

    def test_scan_is_off_main_thread(self):
        self.window.scan()
        self.drain()
        self.assertEqual(self.window.model.rowCount(), 3)
        self.assertTrue(all(thread != threading.get_ident() for thread in self.service.threads))

    def test_paint_and_filter_do_not_read_game_files(self):
        self.window._scanned(self.service.entries)
        with patch.object(games.Game, "installed", new_callable=PropertyMock, side_effect=AssertionError("UI touched disk")):
            self.window.search.setText("Cyberpunk")
            self.app.processEvents()
            self.assertEqual(self.window.proxy.rowCount(), 1)
            self.window.table.viewport().repaint()

    def test_stale_inspection_cannot_replace_selection(self):
        self.service.delays["Control"] = .15
        self.window._scanned(self.service.entries)
        self.window.table.selectRow(0)
        self.window.table.selectRow(1)
        self.drain()
        self.assertEqual(self.window.current.game.name, "Cyberpunk 2077")
        self.assertEqual(self.window.inspection.entry.game.name, "Cyberpunk 2077")

    def test_chinese_english_preserve_settings(self):
        self.select_game()
        self.window.scale_slider.setValue(75)
        old_key = self.window.current.key
        self.window.change_language(1)
        self.app.processEvents()
        self.assertEqual(self.window.current.key, old_key)
        self.assertEqual(self.window.scale_slider.value(), 75)
        self.assertEqual(prefs.get("language"), "en")
        self.assertEqual(self.window.nav_buttons[0].text(), "Game library")
        self.window.change_language(0)
        self.assertEqual(self.window.nav_buttons[0].text(), "游戏库")

    def test_install_uses_snapshot_and_backend_options(self):
        self.select_game()
        selected = self.window.current
        self.window.scale_slider.setValue(70)
        self.window.install_selected()
        self.drain()
        item, options = self.service.installs[0]
        self.assertIs(item, selected)
        self.assertEqual(options.path, dlss.OPTI)
        self.assertEqual(options.nr["WorkingScale"], .7)
        self.assertTrue(item.installed)
        self.assertNotIn(threading.get_ident(), self.service.threads)

    def test_hidden_selection_cannot_be_installed(self):
        self.select_game()
        self.window.search.setText("no-such-game")
        self.assertIsNone(self.window.current)
        self.window.install_selected()
        self.assertFalse(self.service.installs)

    def test_small_window_primary_actions_are_accessible(self):
        self.select_game()
        self.window.resize(900, 620)
        self.app.processEvents()
        self.assertGreaterEqual(self.window.table.columnWidth(0), 200)
        self.window.advanced_toggle.setChecked(True)
        self.app.processEvents()
        for widget in (self.window.install_button, self.window.scan_button, self.window.language):
            self.assertTrue(widget.isVisible())
            position = widget.mapTo(self.window, widget.rect().bottomRight())
            self.assertLessEqual(position.x(), self.window.width())
            self.assertLessEqual(position.y(), self.window.height())

    def test_busy_job_blocks_duplicate_install_and_close(self):
        self.select_game()
        self.window._submit(lambda emit: time.sleep(.15), busy=True)
        self.window.install_selected()
        self.assertFalse(self.service.installs)
        self.window.close()
        self.assertTrue(self.window.isVisible())
        self.drain()

    def test_fault_reenables_controls_and_reports(self):
        self.window._submit(lambda emit: 1 / 0, busy=True)
        self.drain()
        self.assertTrue(self.window.scan_button.isEnabled())
        self.assertIn("ZeroDivisionError", self.window.activity_log.toPlainText())

    def test_backend_contract_rejects_changed_signature(self):
        from tools.check_backend import validate
        with patch.object(installer, "install", lambda: None):
            with self.assertRaisesRegex(RuntimeError, "installer.install"):
                validate()

    def test_existing_manifest_preserves_custom_options(self):
        service = BackendService()
        existing = installer.Options(path=dlss.FEEDER, feed={"work_resolution": 65, "custom": 123})
        item = entry(installed=True)
        support = dlss.Support(options=[dlss.FEEDER], recommended=dlss.FEEDER)
        with patch.object(service, "hardware", return_value=("Test", 120)), \
             patch.object(dlss, "detect", return_value=support), \
             patch.object(dlss, "fit", return_value=(True, "test")), \
             patch.object(installer, "options_from_manifest", return_value=existing), \
             patch.object(installer, "reliability", return_value=("stable", "test")):
            result = service.inspect(item)
        self.assertEqual(result.options.feed, existing.feed)
        self.assertEqual(result.options.path, dlss.FEEDER)

    def test_remix_catalog_builds_with_real_upstream_records(self):
        with patch.object(QDialog, "exec", return_value=0):
            self.window.show_remix()

    def test_preset_ids_and_video_scale_remain_backend_values(self):
        self.select_game()
        self.assertEqual(self.window.video_scale.currentData(), "native")
        self.assertEqual(self.window.video_style.currentData(), 0)
        self.assertEqual(self.window.hdr_combo.currentData(), -1)
        options = self.window._options()
        self.assertEqual(options.feed["hdr"], -1)
        self.assertIsInstance(options.provider, int)

    def test_online_choice_clears_local_override(self):
        self.select_game()
        self.window.local_addon = Path("C:/custom.addon64")
        self.window.version_combos["renodx"].addItem("4.55", "4.55")
        self.window.version_combos["renodx"].setCurrentIndex(1)
        self.window.version_combos["renodx"].activated.emit(1)
        self.assertIsNone(self.window._options().renodx_local)
        self.assertEqual(self.window._options().renodx, "4.55")

    def test_addon_catalog_follows_route_family(self):
        self.select_game()
        self.window.catalog = {"renodx": [{"label": "4.55"}], "renodx_sf": [{"label": "SF-test"}]}
        self.window.route_combo.addItem("SF", dlss.RENODX)
        self.window.route_combo.setCurrentIndex(self.window.route_combo.findData(dlss.RENODX))
        combo = self.window.version_combos["renodx"]
        self.assertGreaterEqual(combo.findData("SF-test"), 0)
        self.assertEqual(combo.findData("4.55"), -1)
        self.window.route_combo.setCurrentIndex(0)
        self.assertGreaterEqual(combo.findData("4.55"), 0)
        self.assertEqual(combo.findData("SF-test"), -1)

    def test_scan_with_stale_inspection_restores_language(self):
        self.select_game()
        self.service.delays["Cyberpunk 2077"] = .2
        self.window.table.selectRow(1)
        self.window.scan()
        self.drain()
        self.assertTrue(self.window.language.isEnabled())

    def test_executable_switch_preserves_library_identity(self):
        original = entry()
        target = original.game.folder / "Bin" / "Win64" / "real.exe"
        original.game.candidates = [original.game.exe, target]
        service = BackendService()
        with patch.object(games, "enrich", side_effect=lambda g, **kwargs: g) as enrich, \
             patch.object(service, "decorate", side_effect=lambda g: LibraryEntry(g, False)):
            changed = service.select_executable(original, target)
        self.assertEqual(changed.key, original.key)
        self.assertEqual(changed.game.source, "Steam")
        self.assertEqual(changed.game.name, original.game.name)
        self.assertEqual(changed.game.exe, target)
        self.assertEqual(changed.game.candidates, original.game.candidates)
        self.assertNotEqual(original.game.exe, target)
        self.assertTrue(enrich.call_args.kwargs["chosen"])

    def test_anticheat_warning_survives_language_change(self):
        self.service.entries[1].anticheat = "BattlEye"
        self.select_game()
        self.assertTrue(self.window.anticheat_warning.isVisible())
        self.assertIn("BattlEye", self.window.model.index(1, 3).data())
        self.assertEqual(self.window.model.index(1, 0).data(Qt.ItemDataRole.ForegroundRole).name(), "#f1a7a2")
        self.window.change_language(1)
        self.app.processEvents()
        self.assertTrue(self.window.anticheat_warning.isVisible())
        self.assertIn("BattlEye", self.window.anticheat_warning.text())

    def test_row_hover_and_icon_fallback(self):
        self.select_game()
        table = self.window.table
        position = table.visualRect(self.window.proxy.index(1, 0)).center()
        QApplication.sendEvent(table.viewport(), QMouseEvent(QEvent.Type.MouseMove, position, table.viewport().mapToGlobal(position), Qt.MouseButton.NoButton, Qt.MouseButton.NoButton, Qt.KeyboardModifier.NoModifier))
        self.app.processEvents()
        self.assertEqual(table.hover_row, 1)
        self.assertFalse(self.window.model.index(0, 0).data(Qt.ItemDataRole.DecorationRole).isNull())

    def test_anticheat_detected_during_decoration(self):
        folder = Path(self.temp.name)
        (folder / "EasyAntiCheat").mkdir()
        game = games.Game(name="Fixture", folder=folder)
        result = BackendService().decorate(game)
        self.assertEqual(result.anticheat, "Easy Anti-Cheat")

    def test_slider_ignores_wheel_but_keeps_keyboard(self):
        from PySide6.QtCore import QPoint, QPointF
        from PySide6.QtGui import QWheelEvent
        self.select_game()
        slider = self.window.scale_slider
        slider.setValue(75)
        position = slider.rect().center()
        for delta in (120, -120):
            event = QWheelEvent(QPointF(position), QPointF(slider.mapToGlobal(position)),
                QPoint(), QPoint(0, delta), Qt.MouseButton.NoButton,
                Qt.KeyboardModifier.NoModifier, Qt.ScrollPhase.NoScrollPhase, False)
            QApplication.sendEvent(slider, event)
            self.assertEqual(slider.value(), 75)
            self.assertFalse(event.isAccepted())
        QTest.keyClick(slider, Qt.Key.Key_Right)
        self.assertEqual(slider.value(), 80)

    def test_closed_combo_ignores_wheel_and_popup_still_selects(self):
        from PySide6.QtCore import QPoint, QPointF
        from PySide6.QtGui import QWheelEvent
        combo = self.window.arch_filter
        position = combo.rect().center()
        for delta in (120, -120):
            event = QWheelEvent(QPointF(position), QPointF(combo.mapToGlobal(position)),
                QPoint(), QPoint(0, delta), Qt.MouseButton.NoButton,
                Qt.KeyboardModifier.NoModifier, Qt.ScrollPhase.NoScrollPhase, False)
            QApplication.sendEvent(combo, event)
            self.assertEqual(combo.currentIndex(), 0)
            self.assertFalse(event.isAccepted())
        combo.showPopup()
        self.app.processEvents()
        view = combo.view()
        QTest.mouseClick(view.viewport(), Qt.MouseButton.LeftButton,
                         pos=view.visualRect(view.model().index(1, 0)).center())
        self.assertEqual(combo.currentIndex(), 1)
        self.assertFalse(view.isVisible())

    def test_transparent_game_icon_uses_placeholder(self):
        from PySide6.QtGui import QImage
        image = QImage(32, 32, QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.transparent)
        self.service.entries[0].icon_image = image
        self.window._scanned(self.service.entries)
        icon = self.window.model.index(0, 0).data(Qt.ItemDataRole.DecorationRole)
        from frontend.icons import usable_image
        self.assertTrue(usable_image(icon.pixmap(32, 32).toImage()))

    def test_game_icon_tries_other_executables(self):
        from PySide6.QtGui import QImage
        from frontend.icons import game_icon
        item = entry()
        other = item.game.folder / "launcher.exe"
        item.game.candidates = [item.game.exe, other]
        image = QImage(32, 32, QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.green)
        with patch("frontend.icons.executable_icon", side_effect=[None, image]) as extract:
            self.assertIs(game_icon(item.game), image)
        self.assertEqual(extract.call_args.args[0], other)

    def test_failed_icon_extraction_is_not_cached(self):
        from types import SimpleNamespace
        from unittest.mock import Mock
        from PySide6.QtGui import QImage
        from frontend import icons
        icons._extract.cache_clear()
        image = QImage(16, 16, QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.green)
        attempts = []
        def extract(path, index, large, small, count):
            attempts.append(path)
            if len(attempts) > 1:
                large._obj.value = 123
            return int(len(attempts) > 1)
        native = SimpleNamespace(shell32=SimpleNamespace(ExtractIconExW=Mock(side_effect=extract)),
                                 user32=SimpleNamespace(DestroyIcon=Mock()))
        with patch.object(icons.ctypes, "windll", native), patch.object(QImage, "fromHICON", return_value=image):
            with self.assertRaises(OSError):
                icons._extract("fixture.exe", 1, 10)
            self.assertTrue(icons.usable_image(icons._extract("fixture.exe", 1, 10)))
            icons._extract("fixture.exe", 1, 10)
        self.assertEqual(len(attempts), 2)
        native.user32.DestroyIcon.assert_called_once()
        icons._extract.cache_clear()

    def test_scan_filters_uninstalled_folder_remnants(self):
        from core import video, library
        folder = Path(self.temp.name)
        live = games.Game(name="Live", folder=folder, exe=folder / "game.exe")
        live.exe.touch()
        empty = games.Game(name="Removed", folder=folder / "empty")
        empty.folder.mkdir()
        (empty.folder / "settings.ini").touch()
        stale = games.Game(name="Stale", folder=folder, exe=folder / "missing.exe")
        service = BackendService()
        events = []
        with patch.object(games, "scan_all", return_value=[live, empty, stale]), \
             patch.object(library, "FILE", folder / "library.json"), \
             patch.object(service, "hardware", return_value=("Test GPU", 120)), \
             patch.object(video, "known", return_value=None), \
             patch.object(service, "decorate", side_effect=lambda g: LibraryEntry(g, False)):
            result = service.scan(lambda *event: events.append(event))
        self.assertEqual([e.game.name for e in result], ["Live"])
        self.assertEqual(len(events), 2)

    def test_opti_build_and_vr_options_follow_route(self):
        self.select_game()
        from dataclasses import replace
        self.window._apply_options(replace(self.window.options, opti_build="wilsjo2", vr=True))
        self.assertEqual(self.window._options().opti_build, "wilsjo2")
        self.assertFalse(self.window._options().vr)
        self.window._combo(self.window.route_combo, dlss.FEEDER)
        self.assertTrue(self.window.vr_check.isEnabled())
        self.window.vr_check.setChecked(True)
        self.assertTrue(self.window._options().vr)
        self.window.current.game.bitness = 32
        self.window._route_changed()
        self.assertFalse(self.window._options().vr)

    def test_ray_reconstruction_only_replaces_existing_supported_game(self):
        self.select_game()
        rr = self.window.version_combos["dlssd"]
        rr.addItem("fixture RR", "fixture")
        self.window._combo(rr, "fixture")
        self.assertFalse(rr.isEnabled())
        self.assertEqual(self.window._options().dlssd, "")
        self.window.inspection.support.evidence.append("nvngx_dlssd.dll")
        self.window._combo(self.window.route_combo, dlss.FEEDER)
        self.assertTrue(rr.isEnabled())
        self.assertEqual(self.window._options().dlssd, "fixture")
        self.window._combo(self.window.route_combo, dlss.OPTI)
        self.assertEqual(self.window._options().dlssd, "")

    def test_driver_warning_visible_before_install(self):
        self.select_game()
        self.window.inspection.driver = "475.14"
        self.window._route_changed()
        self.assertIn("475.14", self.window.engine_warning.text())
        self.assertFalse(self.window.engine_warning.isHidden())
        self.window.inspection.driver = "616.56"
        self.window._route_changed()
        self.assertTrue(self.window.engine_warning.isHidden())

    def test_session_cancel_does_not_apply_and_restores_button(self):
        from frontend.session import SessionResult
        self.select_game(0)
        item = self.window.current
        result = SessionResult("fixture", str(item.game.install_dir), dlss.OPTI, 75, 100)
        with patch.object(self.service, "session_report", return_value=result, create=True), \
             patch.object(self.service, "apply_tune", create=True) as apply, \
             patch.object(QDialog, "exec", return_value=QDialog.DialogCode.Rejected):
            self.window.analyse_session()
            self.assertFalse(self.window.session_button.isEnabled())
            self.drain()
            apply.assert_not_called()
        self.assertTrue(self.window.session_button.isEnabled())

    def test_overlay_key_persists_without_installing(self):
        self.window._combo(self.window.overlay_combo, 0x7A)
        self.window.overlay_combo.activated.emit(self.window.overlay_combo.currentIndex())
        self.assertEqual(prefs.get("overlay_key"), 0x7A)
        self.assertFalse(self.service.installs)

    def test_openxr_cancel_does_not_install(self):
        from PySide6.QtWidgets import QMessageBox
        self.select_game()
        self.window._combo(self.window.route_combo, dlss.FEEDER)
        self.window.vr_check.setChecked(True)
        with patch.object(QMessageBox, "warning", return_value=QMessageBox.StandardButton.No):
            self.window.install_selected()
        self.assertFalse(self.service.installs)
        self.assertIsNone(self.window.busy_job)

    def test_remaining_components_stay_available_for_uninstall(self):
        item = games.Game(name="Removed game", folder=Path(self.temp.name))
        with patch.object(games.Game, "installed", new_callable=PropertyMock, return_value=True):
            self.assertTrue(BackendService.has_game_files(item))

    def test_advanced_settings_fit_narrow_window_with_long_values(self):
        from PySide6.QtWidgets import QScrollArea
        self.select_game()
        w = self.window
        w.resize(900, 620)
        for language in (0, 1):
            w.change_language(language)
            w.advanced_toggle.setChecked(True)
            long_value = "component-version-with-a-very-long-build-name-" * 8
            combo = w.version_combos["renodx"]
            combo.addItem(long_value, long_value)
            combo.setCurrentIndex(combo.count() - 1)
            w.local_file_button.setText(long_value + ".addon64")
            self.app.processEvents()
            scroll = w.detail_stack.findChild(QScrollArea)
            self.assertEqual(scroll.horizontalScrollBar().maximum(), 0)
            self.assertEqual(combo.currentData(), long_value)
            self.assertEqual(combo.toolTip(), long_value)
            self.assertLessEqual(combo.width(), scroll.viewport().width())
            self.assertLessEqual(w.local_file_button.width(), scroll.viewport().width())

    def test_sf_saved_version_and_local_file_survive_inspection(self):
        self.select_game()
        item = self.window.current
        support = dlss.Support(options=[dlss.RENODX], recommended=dlss.RENODX)
        options = installer.Options(path=dlss.RENODX, renodx="pinned-version",
                                    renodx_local=Path("C:/chosen.addon64"))
        inspection = Inspection(item, support, {dlss.RENODX: (True, "")}, options,
                                "Test", "beta", "")
        self.window._inspected(inspection, self.window.selection_generation)
        saved = self.window._options()
        self.assertEqual(saved.renodx, options.renodx)
        self.assertEqual(saved.renodx_local, options.renodx_local)

    def test_opti_scale_preserves_quarter_resolution(self):
        self.select_game()
        self.window._apply_options(installer.Options(path=dlss.OPTI, nr={"WorkingScale": .25}))
        self.assertEqual(self.window._options().nr["WorkingScale"], .25)
        self.window.route_combo.setCurrentIndex(self.window.route_combo.findData(dlss.FEEDER))
        self.assertFalse(self.window.scale_slider.isEnabled())  # DX12 feeder ignores it

    def test_feeder_scale_only_enabled_for_64_bit_dx11(self):
        self.select_game()
        self.window.current.game.api = "DX11"
        self.window.route_combo.setCurrentIndex(self.window.route_combo.findData(dlss.FEEDER))
        self.assertTrue(self.window.scale_slider.isEnabled())
        self.window.current.game.bitness = 32
        self.window._route_changed()
        self.assertFalse(self.window.scale_slider.isEnabled())


    def test_frame_generation_restored_and_disabled_on_other_routes(self):
        self.select_game()
        options = installer.Options(path=dlss.OPTI, fg=True)
        self.window._apply_options(options)
        self.assertTrue(self.window.fg_check.isChecked())
        self.assertTrue(self.window._options().fg)
        self.window.route_combo.setCurrentIndex(self.window.route_combo.findData(dlss.FEEDER))
        self.assertFalse(self.window._options().fg)
        self.window.inspection.mfg_available = True
        self.window._apply_options(installer.Options(path=dlss.FEEDER, mfg=True))
        self.assertTrue(self.window._options().mfg)
        self.window.inspection.mfg_available = False
        self.window._route_changed()
        self.assertFalse(self.window._options().mfg)

    def test_anticheat_decline_does_not_install(self):
        from PySide6.QtWidgets import QMessageBox
        self.select_game()
        self.window.current.anticheat = "Test anti-cheat"
        with patch.object(QMessageBox, "warning", return_value=QMessageBox.StandardButton.No):
            self.window.install_selected()
        self.assertFalse(self.service.installs)
        self.assertIsNone(self.window.busy_job)

    def test_capture_source_is_snapshotted_and_stoppable(self):
        from frontend.backend import video
        self.window.screen_combo.addItems(["screen A", "screen B"])
        with patch.object(video, "known", return_value=entry().game), \
             patch.object(video, "start_screen") as start:
            self.window.video_action("screen")
            self.window.screen_combo.setCurrentIndex(1)
            self.drain()
            self.assertEqual(start.call_args.args[1], "screen A")
        with patch.object(video, "stop_webcam") as stop:
            self.window.video_action("stop")
            self.drain()
            stop.assert_called_once()

    def test_api_override_roundtrip_preserves_game_identity(self):
        from core import pe
        item = entry()
        item.game.folder = Path(self.temp.name)
        item.game.exe = item.game.folder / "game.exe"
        item.game.exe.write_bytes(b"fixture")
        item.game.candidates = [item.game.exe]
        service = BackendService()
        with patch.object(pe, "exe_bitness", return_value=64), \
             patch.object(pe, "detect_api", return_value=("DX12", "test")), \
             patch.object(service, "decorate", side_effect=lambda game: LibraryEntry(game, False)):
            changed = service.set_graphics_api(item, "DX9")
            self.assertEqual(games.api_override(item.game.folder), "DX9")
            self.assertEqual(changed.game.api, "DX9")
            self.assertEqual(changed.key, item.key)
            restored = service.set_graphics_api(changed, "")
            self.assertEqual(restored.game.api, "DX12")
            self.assertEqual(games.api_override(item.game.folder), "")

    def test_scan_feedback_is_immediate_and_prevents_duplicates(self):
        gate = threading.Event()
        def scan(emit):
            gate.wait(2)
            return self.service.entries
        with patch.object(self.service, "scan", side_effect=scan) as worker:
            try:
                self.window.empty_scan_button.click()
                self.assertFalse(self.window.scan_button.isEnabled())
                self.assertIn("扫描中", self.window.scan_button.text())
                self.assertFalse(self.window.empty_scan_button.isEnabled())
                self.assertIn("扫描中", self.window.empty_scan_button.text())
                self.assertTrue(self.window.empty_scan_button._loading_timer.isActive())
                self.window.scan_button.click()
                self.window.empty_scan_button.click()
                self.assertTrue(self.window.scan_feedback.isVisible())
                angle = self.window.scan_button._angle
                QTest.qWait(100)
                self.assertNotEqual(angle, self.window.scan_button._angle)
                self.window.scan()
            finally:
                gate.set()
            self.drain()
            self.assertEqual(worker.call_count, 1)
        self.assertTrue(self.window.scan_button.isEnabled())
        self.assertIsNone(self.window.scan_button._loading_timer)
        self.assertTrue(self.window.empty_scan_button.isEnabled())
        self.assertIsNone(self.window.empty_scan_button._loading_timer)
        self.assertIn("3", self.window.scan_feedback.text())

    def test_scan_failure_preserves_library_and_allows_retry(self):
        self.window._scanned(self.service.entries)
        with patch.object(self.service, "scan", side_effect=RuntimeError("test failure")):
            self.window.scan()
            self.drain()
        self.assertEqual(self.window.model.rowCount(), 3)
        self.assertIn("扫描失败", self.window.scan_feedback.text())
        self.assertTrue(self.window.scan_button.isEnabled())
        self.assertIsNone(self.window.scan_button._loading_timer)
        self.assertTrue(self.window.empty_scan_button.isEnabled())
        self.assertIsNone(self.window.empty_scan_button._loading_timer)
        self.window.scan()
        self.drain()
        self.assertIn("扫描完成", self.window.scan_feedback.text())

    def test_empty_scan_explains_next_step(self):
        with patch.object(self.service, "scan", return_value=[]):
            self.window.scan()
            self.drain()
        self.assertIn("未找到游戏", self.window.scan_feedback.text())
        self.assertIn("手动添加", self.window.scan_feedback.text())
        self.assertTrue(self.window.scan_button.isEnabled())

    def test_install_button_has_progress_and_recovers_after_error(self):
        self.select_game()
        gate = threading.Event()
        def fail(*args):
            gate.wait(2)
            raise RuntimeError("install fixture failure")
        with patch.object(self.service, "install", side_effect=fail) as worker:
            try:
                self.window.install_button.click()
                self.assertFalse(self.window.install_button.isEnabled())
                self.assertTrue(self.window.install_button._loading_timer.isActive())
                self.window.install_button.click()
            finally:
                gate.set()
            self.drain()
            self.assertEqual(worker.call_count, 1)
        self.assertTrue(self.window.install_button.isEnabled())
        self.assertIsNone(self.window.install_button._loading_timer)
        self.assertIn("失败", self.window.status.text())

    def test_inspection_failure_ends_pending_message(self):
        with patch.object(self.service, "inspect", side_effect=RuntimeError("fixture failure")):
            self.window._scanned(self.service.entries)
            self.window.table.selectRow(0)
            self.drain()
        self.assertIn("检查失败", self.window.compatibility.text())
        self.assertFalse(self.window.install_button.isEnabled())
        self.assertIsNone(self.window.inspection)

    def test_update_check_error_restores_button_and_retry(self):
        from frontend import updates
        with patch.object(updates, "check", side_effect=RuntimeError("fixture failure")):
            self.window.update_check_button.click()
            self.assertFalse(self.window.update_check_button.isEnabled())
            self.assertFalse(self.window.language.isEnabled())
            self.assertTrue(self.window.update_check_button._loading_timer.isActive())
            self.drain()
        self.assertFalse(self.window.update_check_running)
        self.assertTrue(self.window.update_check_button.isEnabled())
        self.assertIsNone(self.window.update_check_button._loading_timer)
        self.assertIn("失败", self.window.product_update_status.text())
        with patch.object(updates, "check", return_value=updates.Result("current")):
            self.window.update_check_button.click()
            self.drain()
        self.assertIn("最新版本", self.window.product_update_status.text())

if __name__ == "__main__":
    unittest.main()
