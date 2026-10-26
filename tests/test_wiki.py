import tempfile
import unittest
from pathlib import Path

from agent_foundation.wiki import WikiConflict, WikiPathError, WikiStore


class WikiTests(unittest.TestCase):
    def test_owner_isolation_and_compare_and_swap(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = WikiStore(Path(tmp))
            first = store.write("alice", "long-term/preference.md", "Prefers concise answers", expected_sha256=None, source="user-confirmed")
            self.assertIsNone(store.read("bob", "long-term/preference.md"))
            self.assertEqual([page.path for page in store.search("alice", "concise")], [first.path])
            with self.assertRaises(WikiConflict):
                store.write("alice", first.path, "Changed", expected_sha256=None, source="user")
            updated = store.write("alice", first.path, "Changed", expected_sha256=first.sha256, source="user")
            self.assertNotEqual(first.sha256, updated.sha256)

    def test_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = WikiStore(Path(tmp))
            for path in ("../secret.md", "/tmp/file.md", "private/.hidden.md", "notes.txt", "dir\\file.md"):
                with self.subTest(path=path), self.assertRaises(WikiPathError):
                    store.read("alice", path)


if __name__ == "__main__":
    unittest.main()
