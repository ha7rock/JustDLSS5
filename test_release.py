"""Release integrity checks without network or game writes."""
import io
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch

from tools.prepare_release import collect_notices, fetch, license_path


class ReleaseTests(unittest.TestCase):
    def test_source_paths_cannot_escape_notice_directory(self):
        for name in ("/LICENSE", "root/../LICENSE", "root/C:/LICENSE", "root/..\\LICENSE"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                license_path(name)

    def test_notices_keep_paths_but_do_not_extract_links_or_code(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            archive = root / "source.tar.gz"
            with tarfile.open(archive, "w:gz") as tar:
                for name in ("root/LICENSE", "root/dependency/LICENSE", "root/program.py"):
                    content = b"original notice"
                    entry = tarfile.TarInfo(name)
                    entry.size = len(content)
                    tar.addfile(entry, io.BytesIO(content))
                link = tarfile.TarInfo("root/linked-LICENSE")
                link.type = tarfile.SYMTYPE
                link.linkname = "../../outside"
                tar.addfile(link)
            output = root / "notices"
            self.assertEqual(collect_notices(archive, output), 2)
            self.assertEqual((output / "dependency/LICENSE").read_bytes(), b"original notice")
            self.assertFalse((output / "program.py").exists())
            self.assertFalse((output / "linked-LICENSE").exists())

    def test_bad_download_cannot_replace_cached_source(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            target = root / "fixture-1.tar.gz"
            target.write_bytes(b"old cache")
            source = dict(name="fixture", version="1", url="https://example.invalid/source", sha256="0" * 64)
            with patch("urllib.request.urlopen", return_value=io.BytesIO(b"wrong content")):
                with self.assertRaisesRegex(ValueError, "checksum mismatch"):
                    fetch(source, root)
            self.assertEqual(target.read_bytes(), b"old cache")


if __name__ == "__main__":
    unittest.main()
