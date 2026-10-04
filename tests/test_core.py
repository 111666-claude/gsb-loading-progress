import random
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

    def test_duplicate_report_counts_once(self):
        book = Loading({"a": 1, "b": 1})
        book.report("a")
        book.report("a")
        self.assertEqual(book.progress(), 0.5)

    def test_empty_weights_progress_is_one(self):
        self.assertEqual(Loading({}).progress(), 1.0)

    def test_nonpositive_total_progress_is_one(self):
        book = Loading({"a": 0, "b": 0})
        book.report("a")
        self.assertEqual(book.progress(), 1.0)

    def test_unknown_asset_ignored(self):
        book = Loading({"a": 1, "b": 1})
        book.report("a")
        book.report("ghost")
        self.assertEqual(book.progress(), 0.5)

    def test_progress_is_monotonic_and_bounded(self):
        book = Loading({"a": 2, "b": 3, "c": 5})
        previous = book.progress()
        for asset_id in ("ghost", "a", "a", "b", "ghost", "c", "b"):
            book.report(asset_id)
            current = book.progress()
            self.assertGreaterEqual(current, previous)
            self.assertGreaterEqual(current, 0.0)
            self.assertLessEqual(current, 1.0)
            previous = current
        self.assertEqual(previous, 1.0)

    def test_same_report_sequence_is_reproducible(self):
        def run():
            book = Loading({"a": 1, "b": 2, "c": 3})
            values = []
            for asset_id in ("a", "ghost", "a", "b", "c", "b", "ghost"):
                book.report(asset_id)
                values.append(book.progress())
            return values

        self.assertEqual(run(), run())

    def test_query_cost_does_not_grow_with_queries(self):
        book = Loading({"a-%d" % index: 1 for index in range(3000)})
        for _ in range(3000):
            book.progress()
        self.assertLessEqual(book.scanned_count(), 3000)

    def test_reference_implementation_matches(self):
        rng = random.Random(20261004)
        for _ in range(200):
            size = rng.randint(0, 60)
            weights = {"res-%d" % index: rng.randint(0, 4) for index in range(size)}
            unknown = ["ghost-%d" % index for index in range(6)]
            book = Loading(weights)
            done = set()
            total = sum(weights.values())
            for _ in range(rng.randint(0, 200)):
                pool = list(weights) + unknown
                if not pool:
                    break
                asset_id = rng.choice(pool)
                book.report(asset_id)
                if asset_id in weights:
                    done.add(asset_id)
                if total <= 0:
                    expected = 1.0
                else:
                    expected = sum(weights[asset] for asset in done) / total
                self.assertEqual(book.progress(), expected)

    def test_scale_200k_assets(self):
        size = 200000
        book = Loading({"a-%d" % index: index % 7 + 1 for index in range(size)})
        for index in range(100000):
            if index % 2 == 0:
                book.report("a-%d" % index)
            else:
                book.progress()
        self.assertEqual(book.scanned_count(), 0)
        self.assertLessEqual(book.progress(), 1.0)
        self.assertEqual(len(book.completed), 50000)


if __name__ == "__main__":
    unittest.main()
