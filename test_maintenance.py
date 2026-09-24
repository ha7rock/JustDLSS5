"""Offline safety and interaction gates for upstream 2.0 desktop tools."""
import threading
import time
import unittest
from types import SimpleNamespace as NS
from unittest.mock import patch
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtTest import QTest
from frontend import runtime_tools as rt, pilot
from core import dlss, installer
from test_ui import entry

class MaintenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def drain(self, dialog):
        deadline = time.monotonic() + 5
        while dialog.jobs.active and time.monotonic() < deadline:
            QTest.qWait(20)
        self.assertFalse(dialog.jobs.active)

    def runtime(self):
        with patch.object(rt.QTimer, 'singleShot'):
            return rt.RuntimeDialog(entry().game, True)

    def test_busy_operation_runs_off_gui_and_blocks_duplicate_and_close(self):
        dialog = self.runtime()
        gate = threading.Event()
        threads = []
        def work(emit):
            threads.append(threading.get_ident())
            gate.wait(2)
            return 1
        dialog.show()
        dialog.submit(work, lambda result: None, 'working')
        dialog.submit(lambda emit: self.fail('duplicate'), None, 'duplicate')
        self.assertTrue(all(not b.isEnabled() for b in dialog.actions))
        dialog.reject()
        self.assertTrue(dialog.isVisible())
        gate.set()
        self.drain(dialog)
        self.assertNotEqual(threads[0], threading.get_ident())
        self.assertTrue(all(b.isEnabled() for b in dialog.actions))
        dialog.reject()

    def test_cancel_never_updates_or_restores(self):
        dialog = self.runtime()
        with patch.object(rt.QMessageBox, 'question', return_value=QMessageBox.StandardButton.No), patch.object(rt.dlssupdate, 'update') as update, patch.object(rt.dlssupdate, 'restore') as restore:
            dialog.change(False)
            dialog.change(True)
            update.assert_not_called()
            restore.assert_not_called()
        dialog.reject()

    def test_offline_scan_keeps_restore_available_and_requires_no_catalog(self):
        dialog = self.runtime()
        with patch.object(rt.dlssupdate, 'scan', return_value=[]), patch.object(rt.dlssupdate, 'newest', side_effect=OSError('offline')):
            dialog.refresh()
            self.drain(dialog)
        self.assertIn('offline', dialog.log.toPlainText())
        self.assertTrue(dialog.actions[2].isEnabled())
        with patch.object(rt.QMessageBox, 'question', return_value=QMessageBox.StandardButton.Yes), patch.object(rt.dlssupdate, 'restore', return_value=rt.dlssupdate.Report(done=['restored'])) as restore, patch.object(rt.dlssupdate, 'newest', side_effect=AssertionError('must stay offline')):
            dialog.change(True)
            self.drain(dialog)
            restore.assert_called_once_with(dialog.game)
        self.assertIn('restored', dialog.log.toPlainText())
        dialog.reject()

    def test_refusal_is_visible_not_success(self):
        dialog = self.runtime()
        dialog.changed(rt.dlssupdate.Report(refused='anticheat', error='Anti-cheat detected'))
        self.assertIn('未完成', dialog.status.text())
        self.assertIn('Anti-cheat detected', dialog.log.toPlainText())
        dialog.reject()

    def test_remix_preflight_blocks_removal(self):
        with patch.object(rt.installer, 'preflight', side_effect=RuntimeError('game running')), patch.object(rt.remixdl, 'remove') as remove:
            with self.assertRaisesRegex(RuntimeError, 'game running'):
                rt.remove_remix(entry().game, lambda *args: None)
            remove.assert_not_called()

    def test_openxr_only_offers_removal_for_own_registration(self):
        with patch.object(rt.QTimer, 'singleShot'):
            dialog = rt.OpenXRDialog(True)
        with patch.object(rt.openxr, 'is_ours', return_value=False):
            dialog.scanned([('external.json', 0)])
            self.assertFalse(dialog.remove_button.isEnabled())
        with patch.object(rt.QMessageBox, 'question', return_value=QMessageBox.StandardButton.No), patch.object(rt.openxr, 'unregister') as unregister:
            dialog.remove()
            unregister.assert_not_called()
        dialog.reject()

    def test_community_evidence_reaches_plan_and_explanation(self):
        item = entry(); data = {'games': []}
        inspection = NS(support=NS(options=[dlss.OPTI]), fit={dlss.OPTI:(True, '')}, mfg_available=False)
        with patch.object(installer, 'check_supported', return_value=(True, '')), patch.object(pilot.anticheat, 'detect', return_value=NS(present=False)), patch.object(pilot.community, 'fetch', return_value=data), patch.object(pilot.autopilot, 'plan', return_value=[dlss.OPTI]) as plan, patch.object(pilot.autopilot, 'plan_reasons', return_value=[(dlss.OPTI, '2 of 3 in this game')]), patch.object(pilot.autopilot, 'may_start', return_value=(True, '')):
            result = pilot.prepare(item, installer.Options(path=dlss.OPTI), inspection)
        plan.assert_called_once_with(dlss.OPTI, [dlss.OPTI], data=data, game=item.game)
        self.assertIn('2 of 3', result[2][1])

class WatcherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_closed_event_only_schedules_diagnosis_and_preserves_modal_work(self):
        from frontend.desktop import MainWindow
        from test_ui import FakeService
        service = FakeService()
        with patch('frontend.desktop.prefs.get', side_effect=lambda key, default=None: default), patch('frontend.desktop.prefs.set_'):
            window = MainWindow(service=service, background=False)
            window.model.replace(service.entries)
            window.watch_check.setChecked(True)
            window.watch_events.put(('closed', service.entries[0].game.install_dir, 60))
            with patch.object(window, '_submit') as submit, patch.object(QApplication, 'activeModalWidget', return_value=object()):
                window._watch_tick()
                submit.assert_not_called()
            with patch.object(window, '_submit') as submit, patch.object(QApplication, 'activeModalWidget', return_value=None):
                window._watch_tick()
                submit.assert_called_once()
                work, done = submit.call_args.args
                result = NS(text='recorded session')
                with patch.object(service, 'diagnose', return_value=result, create=True) as diagnose:
                    self.assertIs(work(lambda *args: None), result)
                    diagnose.assert_called_once_with(service.entries[0])
                done(result)
            self.assertTrue(window.watch_report_button.isEnabled())
            self.assertEqual(service.installs, [])
            window.close()

    def test_disabling_stops_watcher_and_discards_pending_events(self):
        from frontend.desktop import MainWindow
        from test_ui import FakeService
        from unittest.mock import Mock
        with patch('frontend.desktop.prefs.get', side_effect=lambda key, default=None: default), patch('frontend.desktop.prefs.set_'):
            window = MainWindow(service=FakeService(), background=False)
            window.watcher = Mock()
            window.watch_events.put(('closed', 'fixture', 60))
            window._watch_changed(False)
            window.watcher.stop.assert_called_once()
            self.assertTrue(window.watch_events.empty())
            window.close()


class Upstream205Tests(unittest.TestCase):
    def test_closing_fault_requires_recent_teardown_not_old_log(self):
        import os
        import tempfile
        from pathlib import Path
        from datetime import datetime, timezone
        from frontend.session import closing_fault
        with tempfile.TemporaryDirectory() as root:
            folder = Path(root)
            log = folder / 'OptiScaler.log'
            log.write_text('ReleaseFeature\nTryDestroyNGXParameters\n')
            stamp = 1780000000
            os.utime(log, (stamp, stamp))
            crash = NS(when=datetime.fromtimestamp(stamp + 1, timezone.utc).strftime('%Y-%m-%d %H:%M:%S'))
            with patch('frontend.session.diagnose._opti_log', return_value=log):
                self.assertTrue(closing_fault(crash, folder, dlss.OPTI))
                self.assertFalse(closing_fault(crash, folder, dlss.FEEDER))
                os.utime(log, (stamp - 60, stamp - 60))
                self.assertFalse(closing_fault(crash, folder, dlss.OPTI))
                log.write_text('QueryCapability\nTryDestroyNGXParameters\n')
                os.utime(log, (stamp, stamp))
                self.assertFalse(closing_fault(crash, folder, dlss.OPTI))

    def test_wrong_package_and_wrong_mfg_variant_are_skipped(self):
        from core import optiscaler
        rows = [{'tag_name':'display-filter', 'assets':[{'name':'display-filter.zip', 'browser_download_url':'https://example.invalid/wrong.zip'}]},
                {'tag_name':'v0.8.5','assets':[
                    {'name':'OptiScaler-NR-v0.8.5-rtx40-mfg.zip','browser_download_url':'https://example.invalid/mfg.zip'},
                    {'name':'OptiScaler-NR-v0.8.5.zip','browser_download_url':'https://example.invalid/standard.zip'}]}]
        with patch.object(optiscaler.sources, 'cached_json', return_value=rows):
            self.assertEqual(optiscaler.archive_name(optiscaler.PRESR), 'OptiScaler-DLSSNR-v0.8.5-standard.zip')
            self.assertEqual(optiscaler.archive_name(optiscaler.PRESR_MFG), 'OptiScaler-DLSSNR-v0.8.5-mfg.zip')
        self.assertTrue(optiscaler.card_refusal(optiscaler.PRESR_MFG, 120))
        self.assertFalse(optiscaler.card_refusal(optiscaler.PRESR_MFG, 89))
        self.assertFalse(optiscaler.card_refusal(optiscaler.PRESR, 120))

    def test_component_notes_keep_distinct_causes(self):
        from frontend.diagnostic_text import translate
        missing = translate('the proxy this install wrote is not in the folder - install again')
        beta = translate("this is a test build - 'newest release' no longer picks one; install again")
        self.assertIn('代理 DLL', missing)
        self.assertIn('测试版', beta)
        self.assertNotEqual(missing, beta)

    def test_user_failed_launch_overrides_unseen_verdict(self):
        from core import diagnose, verdicts
        report = diagnose.Report()
        report.verdict = 'Loaded and set up - confirm in the overlay.'
        corrected = diagnose.answered(report, 'never started', ['nvngx_dlss.dll: updated on the dlss page'])
        self.assertEqual(verdicts.outcome(corrected.verdict), 'failed')
        self.assertIn('undo what the dlss page changed first', corrected.findings[0].detail)
        self.assertIsNone(verdicts.outcome('Unmapped custom outcome'))

    def test_cancelled_user_answer_does_not_change_diagnosis(self):
        from frontend.diagnostic_view import DiagnosticDialog
        from frontend.session import SessionResult
        app = QApplication.instance() or QApplication([])
        dialog = DiagnosticDialog(SessionResult('original','fixture',dlss.FEEDER), 'Fixture', allow_answer=True)
        with patch('frontend.diagnostic_view.QInputDialog.getItem', return_value=('游戏未能启动', False)):
            dialog.ask_started()
        self.assertIsNone(dialog.started_answer)
        self.assertEqual(dialog.raw.toPlainText(), 'original')
        dialog.reject()

    def test_child_launch_restores_dll_search_when_creation_fails(self):
        from core import child
        with patch.object(child.sys, 'frozen', True, create=True), patch.object(child.sys, '_MEIPASS', 'fixture-runtime', create=True), patch.object(child, '_set_dll_directory', return_value=True) as directory, patch.object(child.subprocess, 'Popen', side_effect=OSError('failed')), patch('core.selfupdate.clean_env', return_value={}):
            with self.assertRaises(OSError):
                child.popen(['fixture.exe'])
        self.assertEqual([call.args for call in directory.call_args_list], [(None,), ('fixture-runtime',)])

if __name__ == '__main__':
    unittest.main()