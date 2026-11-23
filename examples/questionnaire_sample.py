"""A small sample of the tax-year 2026 questionnaire and its document rules.

The full questionnaire has about 230 questions. Questions are plain data, so I can review and change
them as a CPA without touching program code. Each question can depend on an earlier answer ("show"),
and each document rule says which answer makes a document required ("when").
"""

TAX_YEAR = 2026

QUESTIONS = [
    {
        "id": "W1",
        "section": "Income",
        "label": "A job as an employee (W-2)",
        "type": "choice",
        "options": [{"value": "yes", "label": "Yes"}, {"value": "no", "label": "No"}],
    },
    {
        "id": "W3",
        "section": "Income",
        "label": "Tips",
        "type": "choice",
        "options": [{"value": "yes", "label": "Yes"}, {"value": "no", "label": "No"}],
        # Only asked when the client said yes to a W-2 job.
        "show": {"key": "W1", "eq": "yes"},
    },
    {
        "id": "W3.occ",
        "section": "Income",
        "label": "Your occupation",
        "type": "text",
        "show": {"key": "W3", "eq": "yes"},
    },
    {
        "id": "W3a",
        "section": "Income",
        "label": "Did you receive tips you did not report to your employer?",
        "type": "choice",
        "options": [
            {"value": "yes", "label": "Yes"},
            {"value": "no", "label": "No"},
            {"value": "unsure", "label": "Not sure"},
        ],
        "show": {"key": "W3", "eq": "yes"},
    },
]

# The client's answers decide their document checklist, so each client only sees what applies to them.
DOCUMENT_RULES = [
    {
        "item": "q2026.W1",
        "accepts": ["W-2"],
        "name": "Form W-2 from every employer",
        "when": {"key": "W1", "eq": "yes"},
        "optional": False,
    },
    {
        "item": "q2026.P12",
        "accepts": ["IRS or state letter"],
        "name": "IRS and state tax notices",
        "when": {"key": "P12", "eq": "yes"},
        "optional": False,
    },
]


def required_documents(answers: dict) -> list[str]:
    """Simple version of the checklist rule, for this sample only."""
    return [rule["name"] for rule in DOCUMENT_RULES if answers.get(rule["when"]["key"]) == rule["when"]["eq"]]


if __name__ == "__main__":
    print(required_documents({"W1": "yes", "P12": "no"}))  # ['Form W-2 from every employer']
