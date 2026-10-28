"""Fail-closed feedback checks, independent of any robot protocol."""

from dataclasses import dataclass
from .planning import finite_vector


@dataclass(frozen=True)
class Feedback:
    measured: tuple
    expected: tuple
    age_s: float


@dataclass(frozen=True)
class GuardLimits:
    max_age_s: float
    max_tracking_error: float
    max_baseline_drift: float

    def __post_init__(self):
        values = finite_vector((self.max_age_s, self.max_tracking_error, self.max_baseline_drift))
        if any(v <= 0 for v in values):
            raise ValueError("All limits must be positive")


@dataclass(frozen=True)
class Decision:
    allowed: bool
    reasons: tuple


def check_feedback(feedback, limits, *, baseline=None):
    """Validate one joint group. Units must match the configured error limits.

    Age must be computed using a trusted local monotonic clock by the caller.
    A successful decision is a data check, not hardware motion authorization.
    """
    reasons = []
    try:
        if not isinstance(limits, GuardLimits):
            raise ValueError("Missing validated limits")
        measured = finite_vector(feedback.measured)
        expected = finite_vector(feedback.expected)
        finite_vector((feedback.age_s,))
        if len(measured) != len(expected):
            raise ValueError("Joint vector lengths differ")
        if feedback.age_s < 0 or feedback.age_s > limits.max_age_s:
            reasons.append("Feedback age is invalid or stale")
        if max(abs(a - b) for a, b in zip(measured, expected)) > limits.max_tracking_error:
            reasons.append("Joint tracking error exceeds the limit")
        if baseline is not None:
            baseline = finite_vector(baseline)
            if len(baseline) != len(measured):
                raise ValueError("Baseline length differs")
            if max(abs(a - b) for a, b in zip(measured, baseline)) > limits.max_baseline_drift:
                reasons.append("Joint drift from the baseline exceeds the limit")
    except (AttributeError, TypeError, ValueError, OverflowError):
        reasons.append("Missing, malformed, or non-finite feedback/configuration")
    return Decision(not reasons, tuple(reasons))
