# Answer key: Too Long

Document: `sample_too_long.txt` (fake sample, 20,553 characters).

This is a bad-input check. There are no clauses to rate.

Expected result:
- The start Lambda rejects it with HTTP 400 before the pipeline runs.
- Error message: `text exceeds 20000 characters`
- The page shows the error. Your page checks the 20,000-character limit itself, so it should show its own message before sending anything.
- No job is created, no AI call is made, and nothing is written to the audit log.

[ ] rejected correctly  [ ] wrongly accepted
