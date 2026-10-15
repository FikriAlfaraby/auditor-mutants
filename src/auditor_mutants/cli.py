"""auditor-mutants inputs | run | score

inputs  write each mutant's policy and trajectory to mutants/<id>/, and the predictions to
        predictions/predictions.json (committed and tagged before any audit runs)
run     audit every mutant with iFixAi's own CLI into runs/<id>/ and collect results/results.json
score   compare the results with the predictions; write results/summary.md
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

from auditor_mutants.mutants import MUTANTS, Mutant, base
from auditor_mutants.policies import POLICIES

ROOT = Path.cwd()


def trace_name(m: Mutant) -> str:
    return "trace.otlp.json" if m.fmt == "otlp" else "trace.jsonl"


def write_inputs(m: Mutant, folder: Path) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    policy = POLICIES[m.policy]().model_dump(mode="json")
    (folder / "policy.json").write_text(
        json.dumps(policy, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    m.build().write(folder / trace_name(m), m.fmt)
    base(m).write(folder / "base.jsonl")  # what the mutant was made from, for showing the change


def prediction(m: Mutant) -> dict[str, object]:
    return {
        "id": m.id,
        "group": m.group,
        "title": m.title,
        "policy": m.policy,
        "format": m.fmt,
        "should": list(m.should),
        "predicted": m.predicted,
        "predicted_violations": sorted(m.predicted_violations),
        "predicted_coverage": sorted(m.predicted_coverage),
        "why": m.why,
    }


def predictions_json() -> str:
    return (
        json.dumps(
            {
                "ifixai_commit": "15599839eccfc2ffcf181b0ca3651413416a9d40",
                "mutants": [prediction(m) for m in MUTANTS],
            },
            indent=1,
            ensure_ascii=False,
        )
        + "\n"
    )


def inputs() -> None:
    for m in MUTANTS:
        write_inputs(m, ROOT / "mutants" / m.id)
    (ROOT / "predictions").mkdir(exist_ok=True)
    (ROOT / "predictions" / "predictions.json").write_text(predictions_json(), encoding="utf-8")
    print(f"{len(MUTANTS)} mutants written to mutants/, predictions to predictions/predictions.json")


def audit(m: Mutant) -> dict[str, object]:
    folder = ROOT / "runs" / m.id
    if folder.exists():
        shutil.rmtree(folder)
    write_inputs(m, folder)
    command = [
        sys.executable,
        "-m",
        "ifixai.cli.main",
        "trajectory",
        "audit",
        str(folder / "policy.json"),
        str(folder / trace_name(m)),
        "--format",
        m.fmt,
        "--output",
        str(folder / "audit"),
    ]
    done = subprocess.run(command, capture_output=True, text=True, check=False)
    report_path = folder / "audit" / "report.json"
    # Read the report, not the exit code: schema and IO errors also exit 1, the same code as BLOCK.
    if not report_path.exists():
        return {
            "id": m.id,
            "decision": "ERROR",
            "violations": [],
            "coverage": [],
            "exit": done.returncode,
            "stderr": done.stderr.strip()[-500:],
        }
    report = json.loads(report_path.read_text(encoding="utf-8"))
    return {
        "id": m.id,
        "decision": report["decision"],
        "exit": done.returncode,
        "violations": sorted({v["code"] for v in report["violations"]}),
        "coverage": sorted({c["code"] for c in report["coverage_issues"]}),
    }


def run() -> None:
    results = [audit(m) for m in MUTANTS]
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results" / "results.json").write_text(json.dumps(results, indent=1) + "\n", encoding="utf-8")
    print(Counter(str(r["decision"]) for r in results))


def verdict(m: Mutant, result: dict[str, object]) -> tuple[bool, bool]:
    """(the auditor's decision is acceptable, my prediction was right in decision and codes)."""
    decision = result["decision"]
    acceptable = decision in m.should
    predicted = (
        decision == m.predicted
        and set(result["violations"]) == set(m.predicted_violations)
        and set(m.predicted_coverage) <= set(result["coverage"])
    )
    return acceptable, predicted


def score() -> None:
    results = {
        r["id"]: r for r in json.loads((ROOT / "results" / "results.json").read_text(encoding="utf-8"))
    }
    lines = [
        "| Mutant | Group | Should | iFixAi | Acceptable | Predicted right | Codes |",
        "|---|---|---|---|---|---|---|",
    ]
    tally: Counter[str] = Counter()
    for m in MUTANTS:
        r = results[m.id]
        acceptable, predicted = verdict(m, r)
        tally[f"{m.group} acceptable"] += acceptable
        tally[f"{m.group} total"] += 1
        tally["predicted right"] += predicted
        codes = ", ".join([*r["violations"], *r["coverage"]]) or "none"
        lines.append(
            f"| {m.id} | {m.group} | {' or '.join(m.should)} | {r['decision']} | {'yes' if acceptable else 'NO'} "
            f"| {'yes' if predicted else 'NO'} | {codes} |"
        )
    head = [
        f"{tally[f'{g} acceptable']} of {tally[f'{g} total']} {g}"
        for g in ("control", "violation", "judgment", "probe")
    ]
    text = (
        "Acceptable decisions: "
        + "; ".join(head)
        + f". Predictions right: {tally['predicted right']} of {len(MUTANTS)}.\n\n"
    )
    text += "\n".join(lines) + "\n"
    (ROOT / "results" / "summary.md").write_text(text, encoding="utf-8")
    print(text)


def main() -> None:
    commands = {"inputs": inputs, "run": run, "score": score}
    if len(sys.argv) != 2 or sys.argv[1] not in commands:
        print(__doc__)
        raise SystemExit(2)
    commands[sys.argv[1]]()


if __name__ == "__main__":
    main()
