"""Invalid arguments must never open the excluded upstream GUI."""
import subprocess
import sys
import unittest
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parent


class CommandLineTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(ROOT / "autopilot_desktop.py"), *args],
                              capture_output=True, text=True, encoding="utf8", timeout=10)

    def test_invalid_arguments_are_rejected(self):
        for args in (("--unknown",), ("--route",), ("--check",), ("--route", "feeder")):
            with self.subTest(args=args):
                result = self.run_cli(*args)
                self.assertEqual(result.returncode, 2)
                self.assertNotIn("Traceback", result.stderr)

    def test_version_identifies_frontend(self):
        result = self.run_cli("--version")
        self.assertEqual(result.returncode, 0)
        self.assertIn("JustDLSS5", result.stdout)

    def test_new_options_reach_upstream_without_starting_gui(self):
        import autopilot_desktop
        for build in ("y4my4my4m", "wilsjo2"):
            args = ["JustDLSS5", "C:/fixture", "--check", "--vr", "--opti-build", build]
            with patch.object(sys, "argv", args), patch("dlss5_autopilot.main", return_value=0) as run:
                self.assertEqual(autopilot_desktop.main(), 0)
                run.assert_called_once()
        self.assertEqual(self.run_cli("C:/fixture", "--opti-build", "invalid").returncode, 2)


if __name__ == "__main__":
    unittest.main()
