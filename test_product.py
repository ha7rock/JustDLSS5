"""Offline checks for release selection and privacy-limited feedback URLs."""
import unittest
from urllib.parse import urlparse, parse_qs
from urllib.error import HTTPError
from unittest.mock import patch
from frontend import feedback, updates


def release(tag, preview=False, draft=False):
    return {"tag_name": tag, "prerelease": preview, "draft": draft}


class ProductTests(unittest.TestCase):
    def test_check_interval_and_invalid_saved_timestamp(self):
        self.assertFalse(updates.check_due(100000, 100001))
        self.assertTrue(updates.check_due(100000, 200000))
        self.assertTrue(updates.check_due("invalid", 200000))
        self.assertTrue(updates.check_due(300000, 200000))

    def test_semantic_order(self):
        result = updates.select_release([release("v0.9.0"), release("v0.10.0")], "0.2.0")
        self.assertEqual(result.version, "v0.10.0")

    def test_channels_and_drafts(self):
        releases = [release("v0.3.0-beta.1", True), release("v1.0.0", draft=True)]
        self.assertEqual(updates.select_release(releases).status, "no_release")
        self.assertEqual(updates.select_release(releases, preview=True).version, "v0.3.0-beta.1")

    def test_downgrade_and_final_version(self):
        self.assertEqual(updates.select_release([release("v0.1.0")], "0.2.0").status, "current")
        self.assertEqual(updates.select_release([release("v0.2.0")], "0.2.0-rc.1").status, "available")

    def test_invalid_metadata_and_host(self):
        self.assertEqual(updates.select_release({}).status, "unavailable")
        self.assertEqual(updates.select_release([release("https://evil.test")]).status, "no_release")
        data = release("v0.3.0")
        data["html_url"] = "https://evil.test"
        self.assertEqual(urlparse(updates.select_release([data]).url).netloc, "github.com")

    def test_private_repo_is_not_up_to_date(self):
        with patch.object(updates, "urlopen", side_effect=HTTPError(updates.API, 404, "private", {}, None)):
            self.assertEqual(updates.check().status, "restricted")

    def test_feedback_uses_form_and_excludes_unknown_fields(self):
        url = feedback.issue_url({"game": "游戏 A & B", "versions": "0.2.0", "log": "secret", "path": "C:/Users/Someone"})
        parsed = urlparse(url)
        values = parse_qs(parsed.query)
        self.assertEqual(parsed.path, "/ha7rock/JustDLSS5/issues/new")
        self.assertEqual(values["game"], ["游戏 A & B"])
        self.assertEqual(values["template"], ["bug-report.yml"])
        self.assertNotIn("secret", url)
        self.assertNotIn("Someone", url)


if __name__ == "__main__":
    unittest.main()
