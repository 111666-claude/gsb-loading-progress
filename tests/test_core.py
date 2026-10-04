import random
import time
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


class WeightedProgressTest(unittest.TestCase):
    def test_weighted_progress_uses_weights(self):
        book = Loading({"a": 3, "b": 1})
        book.report("a")
        self.assertEqual(book.progress(), 0.75)
        book.report("b")
        self.assertEqual(book.progress(), 1.0)

    def test_duplicate_report_is_idempotent(self):
        book = Loading({"a": 1, "b": 1})
        book.report("a")
        before = book.progress()
        for _ in range(100):
            book.report("a")
        self.assertEqual(book.progress(), before)
        self.assertEqual(book.progress(), 0.5)
        self.assertEqual(len(book.reported), 1)

    def test_empty_weights_progress_is_full(self):
        book = Loading({})
        self.assertEqual(book.progress(), 1.0)

    def test_nonpositive_total_progress_is_full(self):
        for weights in ({"a": 0}, {"a": 0, "b": 0}, {"a": -1, "b": 1},
                        {"a": -3}):
            book = Loading(weights)
            book.report("a")
            self.assertEqual(book.progress(), 1.0)

    def test_unknown_assets_are_ignored(self):
        book = Loading({"a": 1, "b": 1})
        for name in ("ghost", "unknown", "nope"):
            book.report(name)
        self.assertEqual(book.progress(), 0.0)
        self.assertEqual(len(book.reported), 0)
        book.report("a")
        for _ in range(50):
            book.report("ghost")
        self.assertEqual(book.progress(), 0.5)

    def test_progress_bounded_and_monotone(self):
        book = Loading({"a": 1, "b": 2, "c": 3})
        sequence = ["a", "a", "ghost", "b", "ghost", "c", "c"]
        previous = 0.0
        for asset_id in sequence:
            book.report(asset_id)
            value = book.progress()
            self.assertGreaterEqual(value, previous)
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)
            previous = value
        self.assertEqual(previous, 1.0)

    def test_same_sequence_is_deterministic(self):
        sequence = ["a", "a", "ghost", "b", "ghost", "a", "b"]
        runs = []
        for _ in range(3):
            book = Loading({"a": 2, "b": 1, "c": 4})
            values = []
            for asset_id in sequence:
                book.report(asset_id)
                values.append(book.progress())
            runs.append(values)
        self.assertEqual(runs[0], runs[1])
        self.assertEqual(runs[1], runs[2])


class QueryCostTest(unittest.TestCase):
    def test_scanned_does_not_grow_with_queries(self):
        book = Loading({"a-%d" % i: 1 for i in range(3000)})
        for _ in range(3000):
            book.progress()
        self.assertLessEqual(book.scanned_count(), 3000)

    def test_reports_and_queries_are_constant_time(self):
        size = 200_000
        book = Loading({"a-%d" % i: 1 for i in range(size)})
        started = time.perf_counter()
        for i in range(100_000):
            book.report("a-%d" % (i % size))
            book.progress()
        elapsed = time.perf_counter() - started
        self.assertEqual(book.progress(), 0.5)
        self.assertLessEqual(book.scanned_count(), size)
        self.assertLess(elapsed, 10.0)


class ReferenceCrossCheckTest(unittest.TestCase):
    @staticmethod
    def reference_progress(weights, events, checkpoints):
        reported = set()
        total = sum(weights.values())
        answers = []
        cursor = 0
        for checkpoint in checkpoints:
            while cursor < checkpoint:
                asset_id = events[cursor]
                if asset_id in weights:
                    reported.add(asset_id)
                cursor += 1
            if total <= 0:
                answers.append(1.0)
            else:
                answers.append(sum(weights[aid] for aid in reported) / total)
        return answers

    def test_matches_reference_over_200_random_runs(self):
        rng = random.Random(20261004)
        for _ in range(200):
            size = rng.randint(1, 40)
            weights = {"a-%d" % i: rng.randint(0, 10) for i in range(size)}
            events = []
            for _ in range(rng.randint(0, 120)):
                pick = rng.randint(0, size + 9)
                events.append("a-%d" % pick if pick < size else "x-%d" % pick)
            checkpoints = sorted({rng.randint(0, len(events))
                                  for _ in range(rng.randint(1, 10))})
            if not checkpoints:
                checkpoints = [len(events)]

            book = Loading(weights)
            expected = self.reference_progress(weights, events, checkpoints)
            actual = []
            checkpoint_set = set(checkpoints)
            for index, asset_id in enumerate(events, start=1):
                book.report(asset_id)
                if index in checkpoint_set:
                    actual.append(book.progress())
            if 0 in checkpoint_set:
                actual.insert(0, book.progress() if not events
                              else Loading(weights).progress())
            self.assertEqual(len(actual), len(expected))
            for got, want in zip(actual, expected):
                self.assertEqual(got, want)


if __name__ == "__main__":
    unittest.main()
