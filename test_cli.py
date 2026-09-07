"""Invalid arguments must never open the excluded upstream GUI."""
import subprocess
import sys
import unittest
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


if __name__ == "__main__":
    unittest.main()
