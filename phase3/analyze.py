"""Phase 3 numbers: how repeatable iFixAi's judge is on replies that never change.

    uv run python phase3/analyze.py

Part A: the scripted refuser's B09 and B18 items, judged in seven runs (phase 2b's two full runs and five
runs of those two inspections). Part B: careful Luna's 20 step-3 goal replies re-judged four ways
(rejudge_b18.py). Every number in phase3/RESULTS.md comes from here, and tests/test_phase3.py holds the
file to them.
"""

from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
PHASE2 = HERE.parent / "phase2" / "runs"
RUNS_A = ("refuser-1", "refuser-2", *(f"refuser-{n}-B09-B18" for n in range(3, 8)))
INSPECTIONS = ("B09", "B18")
REJUDGE = HERE / "runs" / "b18-rejudge.json"


def load(name: str) -> dict:
    return json.loads((PHASE2 / f"{name}.json").read_text(encoding="utf-8"))


def judged(run: dict, tid: str) -> list[dict]:
    test = next(t for t in run["test_results"] if t["test_id"] == tid)
    return [e for e in test["evidence"] if e.get("evaluation_method") == "judge"]


def score(run: dict, tid: str) -> float:
    return next(t for t in run["test_results"] if t["test_id"] == tid)["score"]


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """95% Wilson score interval for k of n."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (max(0.0, centre - half), min(1.0, centre + half))


def same_items(runs: list[dict], tid: str) -> bool:
    """Every run sent the same probes in the same order and recorded the same reply to each."""
    keys = [
        [(e.get("test_case_id"), e.get("prompt_sent"), e.get("actual_response")) for e in judged(r, tid)]
        for r in runs
    ]
    return all(k == keys[0] for k in keys[1:])


def valid(item: dict) -> bool:
    """A judgment that came back. One the judge never answered has no verdict; it is left out, not failed."""
    return item.get("extraction_error") is None


def stability(runs: list[dict], tid: str) -> dict:
    per_run = [judged(r, tid) for r in runs]
    first = per_run[0]
    answered = [[items[i] for items in per_run if valid(items[i])] for i in range(len(first))]
    passes = [sum(e.get("passed") is True for e in v) for v in answered]
    counts = [len(v) for v in answered]
    unstable = sum(0 < k < m for k, m in zip(passes, counts, strict=True))
    # the chance that two of an item's answered runs, picked at random, disagree on it
    disagree = [
        2 * k * (m - k) / (m * (m - 1)) if m > 1 else 0.0 for k, m in zip(passes, counts, strict=True)
    ]
    both = [(a, b) for a, b in zip(per_run[0], per_run[1], strict=True) if valid(a) and valid(b)]
    out = {
        "items": len(first),
        "runs": len(runs),
        "unanswered": sum(len(runs) - m for m in counts),
        "unstable": unstable,
        "unstable_ci": wilson(unstable, len(first)),
        "pass_counts": Counter(passes),
        "expected_disagreements": sum(disagree),
        "scores": [score(r, tid) for r in runs],
        "observed_1_2": sum(a.get("passed") != b.get("passed") for a, b in both),
    }
    if tid == "B09":
        kind = [e["details"]["template_vars"]["violation_type"] for e in first]
        kinds = sorted(set(kind))
        out["by_type"] = {
            k: {
                "pass_rate": sum(p for p, x in zip(passes, kind, strict=True) if x == k)
                / sum(m for m, x in zip(counts, kind, strict=True) if x == k),
                "unstable": sum(0 < p < m for p, m, x in zip(passes, counts, kind, strict=True) if x == k),
                "items": kind.count(k),
            }
            for k in kinds
        }
        # each item's passes and answered runs, grouped by request type in recorded order: what the page draws
        out["passes_by_type"] = {
            k: [[p, m] for p, m, x in zip(passes, counts, kind, strict=True) if x == k] for k in kinds
        }
    if tid == "B18":
        step = [e["step_number"] for e in first]
        out["by_step"] = {
            s: {
                "unstable": sum(0 < p < m for p, m, x in zip(passes, counts, step, strict=True) if x == s),
                "items": step.count(s),
            }
            for s in sorted(set(step))
        }
    return out


def part_a() -> dict:
    runs = [load(n) for n in RUNS_A]
    return {
        "runs": list(RUNS_A),
        "same_items": {tid: same_items(runs, tid) for tid in INSPECTIONS},
        "extra_judge_calls": {
            name: r["judge_stats"]["total_calls"] - sum(len(judged(r, t)) for t in r_tests(r))
            for name, r in zip(RUNS_A, runs, strict=True)
        },
        **{tid: stability(runs, tid) for tid in INSPECTIONS},
    }


def r_tests(run: dict) -> list[str]:
    return [t["test_id"] for t in run["test_results"]]


def part_b() -> dict:
    data = json.loads(REJUDGE.read_text(encoding="utf-8"))
    setups = list(data["setups"])
    out = {"repeats": data["repeats"], "judge_calls": data["judge_calls"], "setups": setups, "groups": {}}

    def group(c: dict) -> str:
        if not c["wrote_story"]:
            return "declined the story"
        return (
            "wrote the story, said it changed"
            if c["recorded"] is False
            else "wrote the story, said it had not"
        )

    convs = data["conversations"]
    out["group_sizes"] = Counter(group(c) for c in convs)
    errors = 0
    for setup in setups:
        rows = []
        for c in convs:
            answered = [j for j in c["judgments"][setup] if j["extraction_error"] is None]
            errors += len(c["judgments"][setup]) - len(answered)
            votes = [j["passed"] for j in answered]
            rows.append(
                {
                    "group": group(c),
                    "passed": sum(votes) * 2 > len(votes) if votes else None,
                    "split": 0 < sum(votes) < len(votes),
                    "recorded": c["recorded"],
                }
            )
        out["groups"][setup] = {
            g: {
                "passed": sum(r["passed"] is True for r in rows if r["group"] == g),
                "of": sum(r["group"] == g for r in rows),
            }
            for g in sorted(out["group_sizes"])
        }
        out.setdefault("same_as_recorded", {})[setup] = sum(r["passed"] == r["recorded"] for r in rows)
        out.setdefault("no_verdict", {})[setup] = sum(r["passed"] is None for r in rows)
        out.setdefault("split", {})[setup] = sum(r["split"] for r in rows)
        out.setdefault("verdicts", {})[setup] = [r["passed"] for r in rows]
    asis = out["verdicts"]["as-is"]
    out["changed_from_as_is"] = {
        s: sum(
            a != b for a, b in zip(asis, out["verdicts"][s], strict=True) if a is not None and b is not None
        )
        for s in setups
    }
    out["extraction_errors"] = errors
    return out


def summary() -> dict:
    return {"part A": part_a(), "part B": part_b()}


if __name__ == "__main__":
    print(json.dumps(summary(), indent=1, default=lambda o: dict(o) if isinstance(o, Counter) else str(o)))
