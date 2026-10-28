"""Synthetic offline example; importing or running this module opens no connections."""

import json
from dataclasses import asdict
from . import Feedback, GuardLimits, check_feedback, plan_translation


def main():
    # Arbitrary demo values, not deployment settings or robot specifications.
    limits = GuardLimits(max_age_s=1.0, max_tracking_error=0.08, max_baseline_drift=0.03)
    fresh = Feedback(measured=(0.01, 0.02), expected=(0.01, 0.02), age_s=0.1)
    stale = Feedback(measured=(0.01, 0.02), expected=(0.01, 0.02), age_s=2.0)
    print(json.dumps({
        "mode": "offline-synthetic",
        "fresh_feedback": asdict(check_feedback(fresh, limits, baseline=(0.0, 0.0))),
        "stale_feedback": asdict(check_feedback(stale, limits)),
        "trajectory": [asdict(p) for p in plan_translation(
            (0.0, 0.0, 0.0), (0.01, 0.0, 0.0), duration_s=2.0, samples=5
        )],
    }, indent=2))


if __name__ == "__main__":
    main()
