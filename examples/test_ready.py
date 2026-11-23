"""Part 5: the "Ready to prepare" box rules. Made-up data only."""

from ready import ready_summary

CLIENT = {"return_id": "r-1"}
YN = [{"value": "yes", "label": "Yes"}, {"value": "no", "label": "No"}]


def q(**changes):
    base = {
        "submitted_at": "2027-01-20T10:00:00Z",
        "submission_notice": None,
        "current_answers": {},
        "schema": {
            "questions": [
                {"id": "P9", "section": "IRS and identity", "label": "Everyone has an SSN?", "type": "choice"},
                {"id": "X3", "section": "Payments", "label": "Medical costs", "type": "choice"},
                {"id": "N.about", "section": "About you", "label": "Note", "type": "textarea"},
            ]
        },
        "required_items": [],
    }
    return {**base, **changes}


def texts(lines):
    return [line["text"] for line in lines]


def test_no_return_no_box():
    assert ready_summary({"return_id": None}, None, None) is None


def test_not_submitted_is_waiting():
    box = ready_summary(CLIENT, None, [])
    assert box["status"] == "waiting" and texts(box["waiting"]) == ["Questionnaire not submitted yet"]


def test_ready_when_everything_is_received_or_explained():
    items = [
        {"name": "Form W-2", "status": "received", "optional": False},
        {"name": "Form 1099-INT", "status": "missing", "optional": False, "note": "not_this_year"},
        {"name": "Receipts", "status": "missing", "optional": True},
    ]
    box = ready_summary(CLIENT, q(required_items=items), [])
    assert box["status"] == "ready" and box["waiting"] == []
    assert texts(box["look"]) == ["Form 1099-INT: client says it doesn't apply in 2026"]


def test_waiting_lines_for_missing_later_and_open_questions():
    items = [
        {"name": "Form W-2", "status": "missing", "optional": False},
        {"name": "Form 1098", "status": "missing", "optional": False, "note": "later", "note_until": "2027-02-01"},
    ]
    qs = [{"file_name": "r.pdf", "question_id": "RT2.roll", "label": "Rolled over?", "options": YN, "answer": None}]
    box = ready_summary(CLIENT, q(required_items=items, submission_notice="x"), qs)
    assert box["status"] == "waiting"
    assert texts(box["waiting"]) == [
        "Questionnaire needs another submit (see Answers)",
        "Form W-2",
        "Form 1098 (client will send it by Feb 1, 2027)",
        "Client to answer a question about r.pdf",
    ]


def test_look_at_unsure_notes_important_no_and_answers():
    answers = {"P9": "no", "X3": "unsure", "N.about": "  Moved in   June  "}
    qs = [
        {"file_name": "b.pdf", "question_id": "tick.I3", "label": "Applies?", "options": YN, "answer": "yes"},
        {"file_name": "c.pdf", "question_id": "tick.I1", "label": "Applies?", "options": YN, "answer": "no"},
        {"file_name": "r.pdf", "question_id": "RT2.roll", "label": "Rolled over?", "options": YN, "answer": "no"},
    ]
    box = ready_summary(CLIENT, q(current_answers=answers), qs)
    assert box["status"] == "ready"
    assert texts(box["look"]) == [
        "Not everyone on the return has a Social Security number or ITIN",
        "Not sure: Medical costs",
        "Note (About you): Moved in June",
        "b.pdf: item wasn't ticked; client says it applies; match the file by hand",
        "c.pdf: item wasn't ticked; client says not theirs; check the file",
        "r.pdf: Rolled over? No",
    ]


def test_long_notes_are_shortened():
    box = ready_summary(CLIENT, q(current_answers={"N.about": "x" * 500}), [])
    assert len(box["look"][0]["text"]) < 200
