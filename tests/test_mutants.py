"""The mutants themselves: valid inputs, the policy iFixAi wrote, and predictions frozen on disk.
No test here runs the audit: the predictions were committed before any mutant was audited."""

import json
from pathlib import Path

import pytest
from ifixai.trajectory.importers import load_otlp_capture
from ifixai.trajectory.integrity import canonical_digest

from auditor_mutants.cli import predictions_json, trace_name
from auditor_mutants.mutants import MUTANTS, base
from auditor_mutants.policies import POLICIES, refund_policy

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("m", MUTANTS, ids=lambda m: m.id)
def test_every_mutant_passes_ifixais_own_schema(m, tmp_path):
    trace = m.build()
    if m.fmt == "otlp":
        capture = load_otlp_capture(trace.write(tmp_path / "t.json", "otlp"))
        assert [e.payload for e in capture.events] == [e.payload for e in trace.hexified().capture().events]
    else:
        trace.capture()
    POLICIES[m.policy]()


def test_the_refund_policy_is_ifixais_own_example():
    # canonical_digest(demo_policy()) from examples/trajectory_assurance.py at iFixAi 1559983
    assert (
        canonical_digest(refund_policy())
        == "747335f2f0bea4c75af2d55e5feba09c1332ac7b376ebc3dd644c3e31287eccc"
    )


def test_mutant_ids_are_unique_and_groups_say_what_should_happen():
    assert len({m.id for m in MUTANTS}) == len(MUTANTS)
    for m in MUTANTS:
        assert m.predicted in ("CLEAR", "BLOCK", "INCONCLUSIVE")
        if m.group in ("control", "probe"):
            assert m.should == ("CLEAR",), m.id
        elif m.group == "violation":
            assert m.should == ("BLOCK",), m.id
        else:
            assert "CLEAR" not in m.should, m.id


@pytest.mark.parametrize("m", MUTANTS, ids=lambda m: m.id)
def test_every_mutant_differs_from_the_trajectory_it_was_made_from(m):
    made_from = base(m)
    made_from.capture()
    if m.group == "control":
        assert made_from.jsonl() == m.build().jsonl()
    elif m.fmt == "jsonl":
        assert made_from.jsonl() != m.build().jsonl(), m.id


def test_predictions_on_disk_are_the_ones_in_the_code():
    assert (ROOT / "predictions" / "predictions.json").read_text(encoding="utf-8") == predictions_json()


@pytest.mark.parametrize("m", MUTANTS, ids=lambda m: m.id)
def test_inputs_on_disk_are_the_ones_the_code_builds(m, tmp_path):
    folder = ROOT / "mutants" / m.id
    m.build().write(tmp_path / trace_name(m), m.fmt)
    assert (folder / trace_name(m)).read_text(encoding="utf-8") == (tmp_path / trace_name(m)).read_text(
        encoding="utf-8"
    )
    assert (folder / "base.jsonl").read_text(encoding="utf-8") == base(m).jsonl()
    policy = json.loads((folder / "policy.json").read_text(encoding="utf-8"))
    assert policy == POLICIES[m.policy]().model_dump(mode="json")
