# Answer key: Empty

Document: `sample_empty.txt` (fake sample, 0 bytes).

This is a bad-input check. There are no clauses to rate.

Expected result:
- The page asks you to paste a document or upload a .txt file first.
- If the empty text still reached the API, the start Lambda would reject it with HTTP 400 and the message `text is required`.
- No job is created, no AI call is made, and nothing is written to the audit log.

[ ] rejected correctly  [ ] wrongly accepted
