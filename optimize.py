# optimize.py
import pulp
from typing import List, Dict, Tuple

def build_shift_masks(shift_templates: Dict[str, Tuple[int,int]],
                      day_intervals: List[str],
                      interval_min: int = 30) -> Dict[str, List[int]]:
    interval_starts = [it for it in day_intervals]
    def ym_to_min(t):
        hh, mm = t.split(":")
        return int(hh)*60 + int(mm)
    starts_min = [ym_to_min(x) for x in interval_starts]
    masks = {}
    for sname, (start_h, end_h) in shift_templates.items():
        smin = start_h * 60
        emin = end_h * 60
        mask = []
        for tmin in starts_min:
            if tmin >= smin and tmin < emin:
                mask.append(1)
            else:
                mask.append(0)
        masks[sname] = mask
    return masks

def optimize_shifts(required_by_interval: List[int],
                    day_interval_labels: List[str],
                    shift_templates: Dict[str, Tuple[int,int]]) -> Dict[str,int]:
    n_intervals = len(required_by_interval)
    masks = build_shift_masks(shift_templates, day_interval_labels)
    model = pulp.LpProblem("shift_coverage", pulp.LpMinimize)
    x = {s: pulp.LpVariable(f"x_{s}", lowBound=0, cat="Integer") for s in shift_templates.keys()}
    model += pulp.lpSum([x[s] for s in x])
    for i in range(n_intervals):
        model += pulp.lpSum([masks[s][i] * x[s] for s in x]) >= required_by_interval[i]
    solver = pulp.PULP_CBC_CMD(msg=False)
    model.solve(solver)
    result = {s: int(pulp.value(x[s])) for s in x}
    return result
