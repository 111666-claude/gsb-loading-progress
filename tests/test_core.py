import unittest

from loading.core import Loading


class LoadingTest(unittest.TestCase):
    def test_progress_starts_at_zero(self):
        self.assertEqual(Loading({"a": 1}).progress(), 0.0)

    def test_report_moves_progress(self):
        book = Loading({"a": 1, "b": 1})
        book.report("a")
        self.assertEqual(book.progress(), 0.5)

    def test_scanned_starts_at_zero(self):
        self.assertEqual(Loading({"a": 1}).scanned_count(), 0)

    def test_missing_asset_keeps_zero(self):
        book = Loading({"a": 1, "b": 1})
        book.report("b")
        book.report("a")
        self.assertEqual(book.progress(), 1.0)


if __name__ == "__main__":
    unittest.main()
