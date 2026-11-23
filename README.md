# Client intake portal for a CPA firm

I'm a CPA. I designed and built a secure client intake system for a small tax firm, using AI coding tools to write the code. This repository is a showcase: a short description, a demo, my key decisions and a few example files. The full project stays private because it belongs to the firm.

## The problem

Every tax season we spent too much time chasing clients for documents and answers. I wanted one place where a client answers the questions, uploads their documents and can see what is still missing, with staff seeing the same picture.

## What it does

**Client portal**
- Sign in with a 6-digit code sent by email
- Fill in a tax questionnaire online, or on a printed form that is scanned back in
- Upload documents and see "Still needed" and "Received"
- Say why a document is missing (doesn't apply this year, can't get it, will send later)

**Staff dashboard**
- Sign in with a password and an authenticator app
- See each client's answers, documents received against documents needed, and an activity history
- A "Ready to prepare" box that shows when a return has everything

**AI document reading**
- AI reads uploaded tax forms (W-2, 1099s) and suggests what each one is and whose it is
- Fixed rules check every suggestion. Anything unclear goes to staff.

## My role

I'm not a programmer. I worked as the product owner:
- Designed the screens and how clients and staff use them
- Wrote the questionnaire (about 230 questions), the document checklists and the rules behind them
- Set the security and privacy rules
- Wrote 687 acceptance checks and tested every step myself on a practice site with made-up data
- Set up the hosting, database and email accounts
- Made and logged every decision

The code was written with Claude and ChatGPT, one step at a time. I explained each step, reviewed the result and tried it myself before accepting it. The project has about 2,900 automated tests.

## Built with

Python (FastAPI) server and background worker, two React (TypeScript) websites, Supabase (database, sign-in, file storage), Render hosting, Postmark email, and AI models for reading documents.

## Demo

See the `media` folder for a short video and screenshots. All data shown is made up.

## Key decisions

See [docs/decisions.md](docs/decisions.md).

## Example files

The `examples` folder has a few small pieces of the project. They are excerpts, so not every file runs on its own.

| File | What it shows |
|---|---|
| `questionnaire_sample.py` | How questions and document rules are written as plain data that a CPA can review |
| `ready.py` and `test_ready.py` | The rules behind the "Ready to prepare" box, with their tests |
| `pdf_lock.py` | Refusing password-locked PDFs at upload, a problem I found while testing |

## Status

Eight of 12 build steps are done. A pilot with a few clients is planned for January 2027, after a security review.
