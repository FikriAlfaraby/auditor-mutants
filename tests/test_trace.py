from auditor_mutants.trace import Event, Trace


def small() -> Trace:
    t = Trace()
    t.add(Event("start", {"kind": "start"}))
    t.add(
        Event(
            "a",
            {
                "kind": "delegation",
                "actor_id": "s",
                "subject_id": "g",
                "action": "refund",
                "resource_scope": "x:*",
                "expires_ns": 10_000,
            },
        )
    )
    t.add(
        Event(
            "b",
            {
                "kind": "action",
                "actor_id": "g",
                "action": "refund",
                "resource": "x:1",
                "arguments_digest": "0" * 64,
                "delegation_id": "a",
            },
        ),
        after="a",
    )
    return t


def test_rows_follow_the_recorder_defaults_and_seal_with_an_end_event():
    rows = small().rows()
    assert [r["event_id"] for r in rows] == ["start", "a", "b", "end"]
    assert [r["sequence"] for r in rows] == [1, 2, 3, 4]
    assert [r["time_ns"] for r in rows] == [100, 101, 102, 103]
    assert [r["parents"] for r in rows] == [[], ["start"], ["a"], ["b"]]
    assert rows[-1]["payload"] == {"kind": "end", "complete": True, "declared_events": 4}


def test_set_none_removes_a_field_and_explicit_times_and_parents_are_kept():
    t = small().set("b", delegation_id=None)
    t.get("b").parents = ("start",)
    t.get("b").time_ns = 100
    row = t.rows()[2]
    assert "delegation_id" not in row["payload"]
    assert (row["parents"], row["time_ns"]) == (["start"], 100)


def test_hexified_renames_every_reference():
    t = small().hexified()
    assert [e.id for e in t.events] == ["0000000000000001", "0000000000000002", "0000000000000003"]
    assert t.get("0000000000000003").payload["delegation_id"] == "0000000000000002"
    t.capture()
