# Key decisions

I logged every decision during the build. These are the main ones.

| Decision | Why |
|---|---|
| Store only the last 4 SSN digits | We don't need the full number to collect documents. What we don't store can't leak. The last 4 is enough to match a form to the right person. |
| AI suggests, rules decide | AI reads forms well but can be wrong. Fixed rules accept or hold each result, and a person checks anything unclear. |
| Made-up data only while practicing | Free plans are fine for testing but not for real tax data. Real clients only after paid, secured plans and a security review. |
| Every rule checked on the server | Hiding a button on the screen isn't security. The server checks every action, and each database table only shows a user their own records. |
| Two-factor sign-in for staff | Staff can see every client, so a password alone isn't enough. |
| Audit log of every change | We can always see who did what and when. |
| Refuse password-locked PDFs at upload | I found that locked brokerage statements were marked "Received" but nobody could open them. Now the client is asked for an unlocked copy right away. |
| Questions and rules as plain data | I can review and update the questionnaire each tax year, without changing program code. |
| Build in 12 steps, one at a time | Nothing moved forward until I had tried the current step myself and was happy with it. |
| Keep the full code private | It belongs to the firm, and publishing it would show anyone how the live system works. |
