"""python3 -m unittest discover -s tests

Stdlib only, like the rest of this. If these pass, the number the report
prints is arithmetic you can check by hand.
"""
import os
import shutil
import tempfile
import unittest


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["COSTCHECK_DIR"] = os.path.join(self.tmp, ".costcheck")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)
        os.environ.pop("COSTCHECK_DIR", None)


class TestUsageExtraction(Base):
    def test_anthropic_shape(self):
        from costcheck.usage import extract

        class U: input_tokens, output_tokens = 100, 20
        class R: usage = U()
        self.assertEqual(extract(R()), (100, 20))

    def test_openai_chat_shape(self):
        from costcheck.usage import extract
        self.assertEqual(extract({"usage": {"prompt_tokens": 7, "completion_tokens": 3}}), (7, 3))

    def test_bare_usage_dict(self):
        from costcheck.usage import extract
        self.assertEqual(extract({"input_tokens": 5, "output_tokens": 1}), (5, 1))

    def test_unknown_shape_raises_with_help(self):
        from costcheck.usage import extract
        with self.assertRaises(ValueError) as cm:
            extract({"tokens": 5})
        self.assertIn("record(input_tokens=", str(cm.exception))


class TestPricing(Base):
    def test_dated_model_id_resolves(self):
        from costcheck.prices import resolve
        self.assertEqual(resolve("claude-3-5-sonnet-20241022"), ("claude-sonnet", True))
        self.assertEqual(resolve("gpt-4o-mini-2024-07-18"), ("gpt-4o-mini", True))

    def test_unknown_model_falls_back_and_says_so(self):
        from costcheck.prices import cost_usd
        usd, exact = cost_usd("some-new-model", 1_000_000, 0)
        self.assertFalse(exact)
        self.assertGreater(usd, 0)      # never silently zero

    def test_arithmetic_is_checkable_by_hand(self):
        from costcheck.prices import cost_usd
        usd, _ = cost_usd("claude-sonnet", 1_000_000, 0)
        self.assertAlmostEqual(usd, 3.00, places=6)


class TestRun(Base):
    def test_success_is_recorded(self):
        import costcheck
        from costcheck.store import read_all
        with costcheck.run(task="t", model="claude-sonnet") as r:
            r.record(input_tokens=1000, output_tokens=100)
            r.succeeded()
        rows = read_all()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["result"], "success")
        self.assertEqual(rows[0]["steps"], 1)

    def test_forgetting_to_call_succeeded_is_a_failure(self):
        import costcheck
        from costcheck.store import read_all
        with costcheck.run(task="t") as r:
            r.record(input_tokens=10, output_tokens=1)
        self.assertEqual(read_all()[0]["result"], "failure")

    def test_exception_still_records_the_money_spent(self):
        import costcheck
        from costcheck.store import read_all
        with self.assertRaises(RuntimeError):
            with costcheck.run(task="t") as r:
                r.record(input_tokens=10_000, output_tokens=1_000)
                raise RuntimeError("boom")
        row = read_all()[0]
        self.assertEqual(row["result"], "failure")
        self.assertGreater(row["cost_usd"], 0)
        self.assertIn("boom", row["reason"])

    def test_model_is_read_from_the_response(self):
        import costcheck
        from costcheck.store import read_all
        with costcheck.run(task="t") as r:
            r.record({"model": "gpt-4o-mini-2024-07-18",
                      "usage": {"prompt_tokens": 1_000_000, "completion_tokens": 0}})
            r.succeeded()
        row = read_all()[0]
        self.assertEqual(row["model"], "gpt-4o-mini-2024-07-18")
        self.assertAlmostEqual(row["cost_usd"], 0.15)      # gpt-4o-mini, not sonnet

    def test_model_you_pass_wins(self):
        import costcheck
        from costcheck.store import read_all
        with costcheck.run(task="t", model="claude-opus") as r:
            r.record({"model": "gpt-4o", "usage": {"input_tokens": 1_000_000, "output_tokens": 0}})
        self.assertAlmostEqual(read_all()[0]["cost_usd"], 15.0)


class TestSummary(Base):
    def _rows(self):
        return [
            {"result": "success", "cost_usd": 1.0, "steps": 5, "duration_s": 15.0,
             "model": "claude-sonnet", "priced_exactly": True},
            {"result": "success", "cost_usd": 1.0, "steps": 5, "duration_s": 15.0,
             "model": "claude-sonnet", "priced_exactly": True},
            {"result": "failure", "cost_usd": 2.0, "steps": 10, "duration_s": 30.0,
             "model": "claude-sonnet", "priced_exactly": True},
        ]

    def test_failures_go_on_top_not_bottom(self):
        from costcheck.report import summarize
        s = summarize(self._rows())
        self.assertAlmostEqual(s["per_request"], 4.0 / 3)
        self.assertAlmostEqual(s["per_success"], 4.0 / 2)      # all spend, only successes
        self.assertGreater(s["per_success"], s["per_request"])

    def test_failed_run_tax(self):
        from costcheck.report import summarize
        s = summarize(self._rows())
        self.assertAlmostEqual(s["waste_share"], 0.5)

    def test_pace_floor_rejects_mocked_calls(self):
        from costcheck.report import summarize
        fast = [{"result": "success", "cost_usd": 0.1, "steps": 10, "duration_s": 0.04,
                 "model": "m", "priced_exactly": True}]
        s = summarize(fast)
        self.assertFalse(s["measured_pace"])       # 4ms per call is not a real call
        self.assertEqual(s["sec_per_step"], 3.0)

    def test_pace_is_used_when_it_is_real(self):
        from costcheck.report import summarize
        s = summarize(self._rows())
        self.assertTrue(s["measured_pace"])
        self.assertAlmostEqual(s["sec_per_step"], 3.0)

    def test_nothing_recorded_is_not_a_crash(self):
        from costcheck.report import render_report, summarize
        self.assertIn("Nothing recorded yet", render_report(summarize([])))


if __name__ == "__main__":
    unittest.main()
