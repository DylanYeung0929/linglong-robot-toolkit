import math
import unittest
from linglong_toolkit import Feedback, GuardLimits, check_feedback, plan_translation


class PlanningTests(unittest.TestCase):
    def test_endpoints_and_monotonicity(self):
        points = plan_translation((0, 0, 0), (1, 2, 3), duration_s=2, samples=21)
        self.assertEqual(points[0].position, (0, 0, 0))
        self.assertEqual(points[-1].position, (1, 2, 3))
        self.assertEqual(points[-1].time_s, 2)
        self.assertTrue(all(a.time_s < b.time_s for a, b in zip(points, points[1:])))
        self.assertTrue(all(0 <= p.position[0] <= 1 for p in points))

    def test_invalid_requests(self):
        for duration in (0, -1, math.nan, math.inf, True):
            with self.subTest(duration=duration), self.assertRaises(ValueError):
                plan_translation((0, 0, 0), (1, 1, 1), duration_s=duration)
        for count in (0, 1, 2.5, True):
            with self.subTest(count=count), self.assertRaises(ValueError):
                plan_translation((0, 0, 0), (1, 1, 1), duration_s=1, samples=count)
        with self.assertRaises(ValueError):
            plan_translation((0, 0), (1, 1, 1), duration_s=1)


class GuardTests(unittest.TestCase):
    limits = GuardLimits(1, 0.08, 0.03)

    def test_valid_and_boundary_feedback(self):
        self.assertTrue(check_feedback(Feedback((0.08,), (0,), 1), self.limits).allowed)

    def test_rejects_bad_feedback(self):
        for feedback in (
            None, Feedback((), (), 0), Feedback((0,), (0, 0), 0),
            Feedback((math.nan,), (0,), 0), Feedback((0,), (0,), math.inf),
            Feedback((0,), (0,), -1), Feedback((0,), (0,), 2),
            Feedback((0.09,), (0,), 0), Feedback((True,), (0,), 0),
        ):
            with self.subTest(feedback=feedback):
                result = check_feedback(feedback, self.limits)
                self.assertFalse(result.allowed)
                self.assertTrue(result.reasons)

    def test_baseline_drift_and_shape(self):
        feedback = Feedback((0.04,), (0.04,), 0)
        self.assertFalse(check_feedback(feedback, self.limits, baseline=(0,)).allowed)
        self.assertFalse(check_feedback(feedback, self.limits, baseline=()).allowed)
        self.assertTrue(check_feedback(feedback, self.limits, baseline=(0.04,)).allowed)

    def test_invalid_limits(self):
        for values in ((0, 1, 1), (1, -1, 1), (1, 1, math.nan)):
            with self.subTest(values=values), self.assertRaises(ValueError):
                GuardLimits(*values)
        self.assertFalse(check_feedback(Feedback((0,), (0,), 0), None).allowed)


if __name__ == "__main__":
    unittest.main()
