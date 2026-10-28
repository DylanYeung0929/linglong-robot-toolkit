"""Position-only smoothstep reference trajectories for offline inspection."""

from dataclasses import dataclass
import math


def finite_vector(values):
    try:
        vector = tuple(values)
        valid = bool(vector) and all(
            not isinstance(v, bool) and isinstance(v, (int, float)) and math.isfinite(v)
            for v in vector
        )
    except (TypeError, OverflowError) as exc:
        raise ValueError("Expected a non-empty vector of finite numbers") from exc
    if not valid:
        raise ValueError("Expected a non-empty vector of finite numbers")
    return vector


@dataclass(frozen=True)
class Waypoint:
    time_s: float
    position: tuple


def plan_translation(start, end, *, duration_s, samples=21):
    """Interpolate two XYZ positions; this does not compute IK or motor commands."""
    start, end = finite_vector(start), finite_vector(end)
    if len(start) != 3 or len(end) != 3:
        raise ValueError("Start and end must contain exactly three coordinates")
    finite_vector((duration_s,))
    if duration_s <= 0:
        raise ValueError("Duration must be positive")
    if isinstance(samples, bool) or not isinstance(samples, int) or samples < 2:
        raise ValueError("At least two integer samples are required")
    points = []
    for index in range(samples):
        u = index / (samples - 1)
        weight = u * u * (3 - 2 * u)
        position = tuple((1 - weight) * a + weight * b for a, b in zip(start, end))
        position = start if index == 0 else end if index == samples - 1 else position
        finite_vector(position)
        points.append(Waypoint(u * duration_s, position))
    return tuple(points)
