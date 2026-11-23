"""One "Ready to prepare" box at the top of the staff client page.

Built on the server from what the page already loads (the reviewed questionnaire and the part 4
questions), so the rules stay in one place. "Waiting" lists what still blocks preparing the return;
"Look at" lists answers a preparer should read first. Each line says which tab holds the details.
"""

import datetime

NOTE = {"not_this_year": "client says it doesn't apply in 2026", "wont_get": "client says they can't get it"}
# Important No answers (plan doc, Part 5).
IMPORTANT_NO = {
    "P9": "Not everyone on the return has a Social Security number or ITIN",
    "H2": "Not everyone had health coverage all year (check the state penalty)",
}


def _day(iso: str | None) -> str:
    try:
        d = datetime.date.fromisoformat(str(iso))
    except ValueError:
        return str(iso)
    return f"{d:%b} {d.day}, {d.year}"


def _short(text: str, limit: int = 160) -> str:
    text = " ".join(str(text).split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def ready_summary(client: dict, questionnaire: dict | None, questions: list[dict] | None) -> dict | None:
    if not client.get("return_id"):
        return None
    waiting: list[dict] = []
    look: list[dict] = []
    submitted = bool(questionnaire and questionnaire.get("submitted_at"))
    if not submitted:
        waiting.append({"text": "Questionnaire not submitted yet", "tab": "answers"})
    if questionnaire:
        if submitted and questionnaire.get("submission_notice"):
            waiting.append({"text": "Questionnaire needs another submit (see Answers)", "tab": "answers"})
        answers = questionnaire.get("current_answers") or {}
        by_id = {q["id"]: q for q in questionnaire.get("schema", {}).get("questions", [])}
        for qid, value in answers.items():
            q = by_id.get(qid)
            if not q:
                continue
            if value == "unsure" or (isinstance(value, list) and "unsure" in value):
                look.append({"text": f"Not sure: {_short(q['label'])}", "tab": "answers"})
            elif q.get("type") == "textarea" and isinstance(value, str) and value.strip():
                look.append({"text": f"Note ({q['section']}): {_short(value)}", "tab": "answers"})
            elif value == "no" and qid in IMPORTANT_NO:
                look.append({"text": IMPORTANT_NO[qid], "tab": "answers"})
        if submitted:
            for item in questionnaire.get("required_items") or []:
                if item.get("status") == "received":
                    continue
                note = item.get("note")
                if note in NOTE:
                    look.append({"text": f"{item['name']}: {NOTE[note]}", "tab": "documents"})
                elif not item.get("optional"):
                    later = f" (client will send it by {_day(item.get('note_until'))})" if note == "later" else ""
                    waiting.append({"text": f"{item['name']}{later}", "tab": "documents"})
    for q in questions or []:
        name = q.get("file_name") or "a file"
        if not isinstance(q.get("answer"), str):
            waiting.append({"text": f"Client to answer a question about {name}", "tab": "documents"})
            continue
        label = next((o["label"] for o in q.get("options", []) if o.get("value") == q["answer"]), q["answer"])
        if str(q.get("question_id", "")).startswith("tick."):
            meaning = "it applies; match the file by hand" if q["answer"] == "yes" else "not theirs; check the file"
            look.append({"text": f"{name}: item wasn't ticked; client says {meaning}", "tab": "documents"})
        else:
            look.append({"text": f"{name}: {_short(q.get('label', ''), 90)} {label}", "tab": "documents"})
    return {"status": "waiting" if waiting else "ready", "waiting": waiting, "look": look}
