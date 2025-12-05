# staffing.py

print("Loading staffing.py from:", __file__)

import math
from typing import List, Dict, Tuple

def erlang_c_probability_of_wait(a: float, c: int) -> float:
    """
    Returns Erlang C probability of wait (Pw) for offered load a and servers c.
    Assumes c > a (if c <= a, returns 1.0)
    """
    if c <= a:
        return 1.0

    # compute P0
    sum_terms = 0.0
    for k in range(c):
        sum_terms += (a**k) / math.factorial(k)
    last_term = (a**c) / (math.factorial(c) * (1.0 - a / c))
    p0 = 1.0 / (sum_terms + last_term)

    pw = last_term * p0
    return pw

def service_level_from_pw(pw: float, c: int, a: float, aht_sec: float, target_secs: float) -> float:
    """
    Given Pw (probability of waiting), returns probability that wait <= target_secs,
    assuming exponential service times.
    SL = 1 - Pw * exp(-(c - a) / aht * target_secs)
    """
    if c <= a:
        return 0.0
    exponent = - (c - a) / aht_sec * target_secs
    sl = 1.0 - pw * math.exp(exponent)
    return max(0.0, min(1.0, sl))

def required_agents_for_interval(volume: int, aht_sec: float, interval_sec: int,
                                 target_sl: float, target_wait_sec: float,
                                 max_extra: int = 200) -> int:
    """
    Iteratively find the minimal integer number of agents c such that
    service level >= target_sl. Uses Erlang-C with offered load:
      a = (volume * aht_sec) / interval_sec
    Returns c (before shrinkage).
    """
    if volume == 0:
        return 0

    a = (volume * aht_sec) / interval_sec  # offered load for that interval
    c = max(1, math.ceil(a))  # start at ceil(a)
    while True:
        # safety cap
        if c > math.ceil(a) + max_extra:
            return c
        pw = erlang_c_probability_of_wait(a, c)
        sl = service_level_from_pw(pw, c, a, aht_sec, target_wait_sec)
        if sl >= target_sl:
            return c
        c += 1

def staffing_from_forecast(forecast_intervals: List[Dict],
                           aht_sec: float,
                           interval_sec: int,
                           target_sl: float,
                           target_wait_sec: float,
                           shrinkage: float = 0.25) -> List[Dict]:
    """
    Input forecast_intervals: list of dicts containing at least:
      {"interval_start": "...", "interval_end":"...", "volume": int}
    Returns list with required agents per interval after applying shrinkage and ceiling.
    """
    results = []
    for row in forecast_intervals:
        vol = int(row.get("volume", 0))
        c = required_agents_for_interval(vol, aht_sec, interval_sec, target_sl, target_wait_sec)
        # apply shrinkage
        if shrinkage >= 1.0:
            net = c
        else:
            net = math.ceil(c / (1.0 - shrinkage))
        results.append({
            "interval_start": row.get("interval_start"),
            "interval_end": row.get("interval_end"),
            "volume": vol,
            "raw_required": c,
            "required_after_shrinkage": net
        })
    return results