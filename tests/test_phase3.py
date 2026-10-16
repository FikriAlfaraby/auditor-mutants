"""Every number in phase3/RESULTS.md, recomputed from the recorded runs and re-judgments."""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# phase3/ is a folder of scripts, not a package: load analyze.py by its path
_spec = importlib.util.spec_from_file_location("analyze3", ROOT / "phase3" / "analyze.py")
analyze = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(analyze)

FLAT = " ".join((ROOT / "phase3" / "RESULTS.md").read_text(encoding="utf-8").split())
S = analyze.summary()
A, B = S["part A"], S["part B"]
B09, B18 = A["B09"], A["B18"]


def says(text: str) -> None:
    assert " ".join(text.split()) in FLAT, text


def pct(x: float) -> str:
    return f"{round(x * 100)}"


def test_nothing_but_the_judge_changes():
    assert A["same_items"] == {"B09": True, "B18": True}
    assert B09["runs"] == B18["runs"] == 7 and B09["unanswered"] == B18["unanswered"] == 0
    says("All seven runs sent the same probes in the same order and recorded the same reply, item for item")


def test_part_a_table():
    says(f"| Items, each judged 7 times | {B09['items']} | {B18['items']} |")
    says(f"| Got both verdicts | {B09['unstable']} | {B18['unstable']} |")
    says(f"| Passed all 7 times | {B09['pass_counts'].get(7, 0)} | {B18['pass_counts'].get(7, 0)} |")
    says(f"| Failed all 7 times | {B09['pass_counts'].get(0, 0)} | {B18['pass_counts'].get(0, 0)} |")
    says(
        f"| Score, lowest and highest run | {min(B09['scores']):.2f} and {max(B09['scores']):.2f} "
        f"| {min(B18['scores']):.2f} and {max(B18['scores']):.2f} |"
    )
    low, high = B09["unstable_ci"]
    says(
        f"{B09['unstable']} of the {B09['items']} policy items got both verdicts: "
        f"{pct(B09['unstable'] / B09['items'])} percent, with a 95% interval of {pct(low)} to {pct(high)} percent"
    )
    says("| B09 items | " + " | ".join(str(B09["pass_counts"].get(k, 0)) for k in range(8)) + " |")
    says(
        f"two runs picked at random disagree on about {round(B09['expected_disagreements'])} of the 120 items; "
        f"runs 1 and 2 disagreed on {B09['observed_1_2']}"
    )


def test_by_request_type():
    rows = {
        "unauthorized_access": "Access the user is not allowed",
        "unauthorized_override": "Override a governance rule",
        "confidence_threshold": "Speculate without saying so (no topic named)",
        "citation_required": "Answer without sources (no topic named)",
    }
    for key, label in rows.items():
        t = B09["by_type"][key]
        says(f"| {label} | {pct(t['pass_rate'])}% | {t['unstable']} of {t['items']} |")
    rates = {k: v["pass_rate"] for k, v in B09["by_type"].items()}
    assert (
        rates["unauthorized_access"]
        > rates["unauthorized_override"]
        > max(rates["citation_required"], rates["confidence_threshold"])
    )


def test_b18_only_step_2_splits():
    steps = B18["by_step"]
    assert steps[2] == {"unstable": 10, "items": 10}
    assert steps[1]["unstable"] == steps[3]["unstable"] == 0
    says("all 10 of its items got both verdicts, and no step-1 or step-3 item ever did")


def test_retries_do_not_explain_it():
    extra = sum(A["extra_judge_calls"].values())
    says(f"it made {extra} calls more than it judged items")
    says(
        f"at most {extra} item judgments involved a retry, and at least {B09['unstable'] - extra} of the 103"
    )


def test_part_b():
    assert B["extraction_errors"] == 0 and all(v == 0 for v in B["no_verdict"].values())
    groups = ("wrote the story, said it changed", "wrote the story, said it had not", "declined the story")
    assert [B["group_sizes"][g] for g in groups] == [15, 4, 1]
    for setup in B["setups"]:
        says(f"| {setup} | " + " | ".join(str(B["groups"][setup][g]["passed"]) for g in groups) + " |")
    assert B["same_as_recorded"]["as-is"] == 20
    says("The rubric as it is repeated all 20 recorded verdicts")
    assert B["changed_from_as_is"]["conversation"] == B["changed_from_as_is"]["no premise"] == 0
    assert B["split"] == {"as-is": 0, "conversation": 0, "no premise": 0, "honest goal": 1}
    says("One reply split 2 to 1 under the honest-goal rubric")
    assert B["judge_calls"] == 240 + 72
    says("72 of the first 240 judgments never came back")


def test_the_predictions():
    says("## The predictions: 9 of 10 held")
    says("103 of the 120 policy items got both verdicts; I had said at least 50")
    says(
        f"Two runs would disagree on about {round(B09['expected_disagreements'])} items; I had said 25 to 50"
    )
    assert 25 <= B09["expected_disagreements"] <= 50 and B09["unstable"] >= 50
    assert all(0.45 <= s <= 0.65 for s in B09["scores"])
