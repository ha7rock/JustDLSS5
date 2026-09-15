"""Game library interaction and artwork identity regressions; no live downloads."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QColor
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from core import prefs, games
from frontend.covers import exact_match, steam_id, load_cover, search_id, clean_name, best_match, prepare_artwork
from frontend.desktop import MainWindow
from test_ui import FakeService, entry


class ArtworkTests(unittest.TestCase):
    def test_packaging_cleanup_preserves_game_identity(self):
        self.assertEqual(clean_name("Resident_Evil_4_(Demo)_[DODI Repack]_v1.2"), "Resident Evil 4 Demo")
        self.assertEqual(best_match([{"id": 1, "name": "Control Ultimate Edition"}], "Control [Repack]"), "1")
        self.assertEqual(best_match([{"id": 2, "name": "Cyberpunk 2077"}], "Cyberpnuk 2077"), "2")
        for query, candidate in [("Control", "Star Control"), ("Resident Evil 4", "Resident Evil 5"),
                                 ("Resident Evil IV", "Resident Evil V"), ("Control Demo", "Control"),
                                 ("Monster Hunter", "Monster Hunter Stories")]:
            self.assertIsNone(best_match([{"id": 1, "name": candidate}], query))
        self.assertIsNone(best_match([{"id": 1, "name": "Control"}, {"id": 2, "name": "Control Ultimate Edition"}], "Control"))

    def test_landscape_keeps_both_edges_and_fills_backdrop(self):
        image = QImage(400, 200, QImage.Format.Format_RGB32)
        image.fill(QColor("#3478ab"))
        for y in range(200):
            image.setPixelColor(0, y, QColor("red"))
            image.setPixelColor(399, y, QColor("green"))
        prepared = prepare_artwork(image)
        self.assertEqual((prepared.width(), prepared.height()), (400, 600))
        self.assertEqual(prepared.pixelColor(0, 300), QColor("red"))
        self.assertEqual(prepared.pixelColor(399, 300), QColor("green"))
        self.assertGreater(prepared.pixelColor(200, 20).blue(), 30)
        portrait = QImage(400, 600, QImage.Format.Format_RGB32)
        portrait.fill(QColor("yellow"))
        self.assertEqual(prepare_artwork(portrait), portrait)

    def test_chinese_search_and_folder_alias(self):
        import json
        game = games.Game("未知显示名", Path("Control"))
        results = [{"items": []}, {"items": []}, {"items": [{"id": 870780, "name": "Control™"}]}]
        with patch("frontend.covers.fetch", side_effect=[json.dumps(r).encode() for r in results]) as fetch:
            self.assertEqual(search_id(game), "870780")
            self.assertIn("l=schinese", fetch.call_args_list[1].args[0])

    def test_local_poster_works_without_a_store_id_or_network(self):
        with tempfile.TemporaryDirectory() as temp:
            image = QImage(600, 900, QImage.Format.Format_RGB32)
            image.fill(QColor("#123456"))
            image.save(str(Path(temp) / "poster.png"))
            with patch("frontend.covers.fetch") as fetch:
                result = load_cover(games.Game("Test", Path(temp)), network=False, cache=Path(temp) / "cache")
                self.assertFalse(result.isNull())
                fetch.assert_not_called()

    def test_match_never_confuses_sequels_or_ambiguous_titles(self):
        rows = [{"id": 1, "name": "Star Control"}, {"id": 2, "name": "Control 2"}]
        self.assertIsNone(exact_match(rows, "Control"))
        rows.append({"id": 3, "name": "Control"})
        self.assertEqual(exact_match(rows, "CONTROL"), "3")
        rows.append({"id": 4, "name": "Control"})
        self.assertIsNone(exact_match(rows, "Control"))
        self.assertEqual(exact_match([{"id": 9, "name": "黑神话：悟空"}], "黑神话 悟空"), "9")

    def test_steam_manifest_identity_and_offline_cache(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            steam = root / "steamapps"
            folder = steam / "common/Control"
            folder.mkdir(parents=True)
            (steam / "appmanifest_12.acf").write_text('"appid" "12" "installdir" "Control"')
            game = games.Game("Different display name", folder)
            self.assertEqual(steam_id(game), "12")
            with patch("frontend.covers.fetch") as fetch:
                self.assertTrue(load_cover(game, network=False, cache=root / "cache").isNull())
                fetch.assert_not_called()

    def test_invalid_custom_art_does_not_silently_download_a_replacement(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch("frontend.covers.fetch") as fetch:
                image = load_cover(games.Game("Test", Path(temp)), str(Path(temp) / "missing.png"))
                self.assertTrue(image.isNull())
                fetch.assert_not_called()

    def test_custom_art_is_decoded_without_network(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "cover.png"
            image = QImage(600, 900, QImage.Format.Format_RGB32)
            image.fill(QColor("#345678"))
            image.save(str(path))
            with patch("frontend.covers.fetch") as fetch:
                cover = load_cover(games.Game("Test", Path(temp)), str(path))
                self.assertEqual((cover.width(), cover.height()), (400, 600))
                fetch.assert_not_called()


class LibraryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.app.setStyle("Fusion")

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.patch = patch.object(prefs, "FILE", Path(self.temp.name) / "settings.json")
        self.patch.start()
        self.window = MainWindow(FakeService(), background=False)
        self.window.show()
        self.entries = [entry("Control", True), entry("Portal"), entry("Long game title " * 12)]
        self.entries[1].game.source = "GOG"
        self.entries[2].anticheat = "EAC"
        self.window._scanned(self.entries)
        self.app.processEvents()

    def drain(self):
        for _ in range(100):
            if not self.window.jobs.active:
                break
            QTest.qWait(20)
        self.app.processEvents()

    def tearDown(self):
        self.drain()
        self.window.close()
        self.app.processEvents()
        self.patch.stop()
        self.temp.cleanup()

    def test_combined_filters_and_reset(self):
        w = self.window
        w.installed_filter.setCurrentIndex(2)
        w._combo(w.source_filter, "GOG")
        w.search.setText("portal")
        self.assertEqual(w.proxy.rowCount(), 1)
        w.search.setText("missing")
        self.assertEqual(w.library_state.currentIndex(), 1)
        self.assertTrue(w.empty_clear_button.isVisible())
        w.empty_clear_button.click()
        self.assertEqual(w.proxy.rowCount(), 3)
        w.installed_filter.setCurrentIndex(3)
        self.assertEqual(w.proxy.index(0, 0).data(Qt.ItemDataRole.UserRole).anticheat, "EAC")

    def test_favorite_and_recent_sort(self):
        w = self.window
        w.model.metadata[self.entries[1].key]["favorite"] = True
        w._library_sort(save=False)
        self.assertEqual(w.proxy.index(0, 0).data(Qt.ItemDataRole.UserRole).game.name, "Portal")
        w.installed_filter.setCurrentIndex(4)
        self.assertEqual(w.proxy.rowCount(), 1)
        w._clear_library_filters()
        w.model.metadata[self.entries[0].key]["recent"] = 99
        w._combo(w.sort_combo, "recent")
        self.assertEqual(w.proxy.index(1, 0).data(Qt.ItemDataRole.UserRole).game.name, "Control")

    def test_switch_views_rescan_and_filter_selection(self):
        w = self.window
        index = w.proxy.index(0, 0)
        w.grid.setCurrentIndex(index)
        self.drain()
        selected = w.current.key
        w.view_combo.setCurrentIndex(1)
        self.assertEqual(w.table.currentIndex().row(), index.row())
        self.assertEqual(w.current.key, selected)
        w._scanned(self.entries)
        self.drain()
        self.assertEqual(w.current.key, selected)
        w.search.setText("no match")
        self.assertIsNone(w.current)
        self.assertFalse(w.detail_stack.isVisible())

    def test_narrow_grid_and_language(self):
        w = self.window
        for language in (0, 1):
            w.change_language(language)
            w.resize(900, 620)
            self.app.processEvents()
            self.assertEqual(w.grid.horizontalScrollBar().maximum(), 0)
            self.assertGreater(w.grid.viewport().width(), 172)
            self.assertEqual(w.proxy.rowCount(), 3)
            # Exercise custom paint for selected/hovered/risk/fallback cards.
            self.assertFalse(w.grab().isNull())


if __name__ == "__main__":
    unittest.main()
