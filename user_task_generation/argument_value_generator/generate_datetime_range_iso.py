# argument_value_generator.py
from __future__ import annotations
import random
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Tuple, Literal

# Cache to keep start/end consistent across separate calls in the same task
_DT_PAIR_CACHE: Dict[str, Tuple[datetime, datetime]] = {}

def _local_tz():
    return datetime.now().astimezone().tzinfo

def _round_dt(dt: datetime, minutes: Optional[int]) -> datetime:
    if not minutes or minutes <= 1:
        return dt.replace(second=0, microsecond=0)
    dt = dt.replace(second=0, microsecond=0)
    m = (dt.minute // minutes) * minutes  # floor to interval
    return dt.replace(minute=m)

def _business_hours_weight(dt: datetime) -> float:
    # Prefer weekday hours ~ 9–17
    hour = dt.hour
    weekday = dt.weekday()  # 0=Mon ... 6=Sun
    in_hours = 9 <= hour <= 17
    base = 1.0 if in_hours else 0.4
    # Weekend penalty
    if weekday >= 5:
        base *= 0.75
    # Slightly prefer mid-morning/early afternoon
    peak = 13  # 1pm
    base *= max(0.6, 1.0 - abs(hour - peak) * 0.05)
    return base

def generate_datetime_range_iso(
    return_field: Literal["start","end","both"] = "start",
    min_minutes_from_now: int = 30,
    max_minutes_from_now: int = 7*24*60,   # 1 week
    duration_minutes_options: Optional[list[int]] = None,
    min_duration_minutes: int = 15,
    max_duration_minutes: int = 90,
    round_to_minutes: Optional[int] = 5,
    business_hours_weight: float = 0.6,    # 0..1; 0 = no bias
    tz: Literal["local","UTC"] = "local",
    pair_key: Optional[str] = None,
    seed: Optional[int] = None,
) -> str:
    """
    Generate a realistic ISO 8601 datetime range.
    - Use the same `pair_key` across two calls (start/end) to keep them consistent.
    - If `return_field="both"`, returns "START|END" (ISO strings joined by a pipe).
    """

    rng = random.Random(seed)
    tzinfo = timezone.utc if tz.upper() == "UTC" else _local_tz()
    now = datetime.now(tzinfo).replace(second=0, microsecond=0)

    # Reuse cached pair if present
    if pair_key and pair_key in _DT_PAIR_CACHE:
        start_dt, end_dt = _DT_PAIR_CACHE[pair_key]
    else:
        # Clamp inputs
        min_m = max(0, int(min_minutes_from_now))
        max_m = max(min_m + 1, int(max_minutes_from_now))

        # Sample a start time; optionally bias toward business hours
        candidates = []
        for _ in range(8):
            delta_m = rng.randint(min_m, max_m)
            cand = now + timedelta(minutes=delta_m)
            candidates.append(cand)

        if business_hours_weight > 0:
            scored = [
                (c, (1.0 - business_hours_weight) + business_hours_weight * _business_hours_weight(c))
                for c in candidates
            ]
            # Weighted pick
            total = sum(w for _, w in scored)
            r = rng.uniform(0, total)
            upto = 0.0
            start_dt = candidates[0]
            for c, w in scored:
                upto += w
                if r <= upto:
                    start_dt = c
                    break
        else:
            start_dt = rng.choice(candidates)

        start_dt = _round_dt(start_dt, round_to_minutes)

        # Duration
        if duration_minutes_options:
            dur = int(rng.choice(duration_minutes_options))
        else:
            dur = rng.randint(int(min_duration_minutes), int(max_duration_minutes))

        end_dt = start_dt + timedelta(minutes=dur)

        if pair_key:
            _DT_PAIR_CACHE[pair_key] = (start_dt, end_dt)

    # Formatters
    def fmt(dt: datetime) -> str:
        # Example: 2025-10-06T14:30-07:00  (includes TZ offset or +00:00 for UTC)
        return dt.isoformat(timespec="minutes")

    if return_field == "start":
        return fmt(start_dt)
    if return_field == "end":
        return fmt(end_dt)
    # "both" -> join for single-field use
    return f"{fmt(start_dt)}|{fmt(end_dt)}"
