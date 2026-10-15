"""The recorded results, reproduced by iFixAi's auditor on the committed inputs, and the numbers the
README quotes, recomputed from them."""

import json
import re
from pathlib import Path

import pytest
from ifixai.trajectory.audit import audit_trajectory
from ifixai.trajectory.importers import load_jsonl_capture, load_otlp_capture

from auditor_mutants.cli import trace_name, verdict
from auditor_mutants.mutants import MUTANTS
from auditor_mutants.policies import POLICIES

ROOT = Path(__file__).resolve().parents[1]
RESULTS = {r["id"]: r for r in json.loads((ROOT / "results" / "results.json").read_text(encoding="utf-8"))}


@pytest.mark.parametrize("m", MUTANTS, ids=lambda m: m.id)
def test_the_recorded_result_is_what_the_auditor_says_today(m):
    path = ROOT / "mutants" / m.id / trace_name(m)
    capture = load_otlp_capture(path) if m.fmt == "otlp" else load_jsonl_capture(path)
    report = audit_trajectory(capture, POLICIES[m.policy]())
    recorded = RESULTS[m.id]
    assert report.decision == recorded["decision"]
    assert sorted({v.code for v in report.violations}) == recorded["violations"]
    assert sorted({c.code for c in report.coverage_issues}) == recorded["coverage"]


def test_the_readme_table_is_the_results():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for group in ("violation", "control", "probe", "judgment"):
        mutants = [m for m in MUTANTS if m.group == group]
        acceptable = sum(verdict(m, RESULTS[m.id])[0] for m in mutants)
        row = re.search(rf"^\| {group} \([^)]*\) \| (\d+) \| (\d+) \|$", readme, re.MULTILINE)
        assert row and (int(row[1]), int(row[2])) == (len(mutants), acceptable), group
    assert all(verdict(m, RESULTS[m.id])[1] for m in MUTANTS), "a prediction missed; the README says 43 of 43"
