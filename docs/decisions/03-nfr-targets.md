# Non-Functional Requirements

**Date**: 2026-11-20 | **Author**: suman manyam | **Status**: Draft

| ID | Area | Target |
|---|---|---|
| NFR-1 | Speed | Result in under 2 minutes for a typical sample document (about 3 pages, under 2,000 words, expected 30-60s) |
| NFR-2 | Input limit | Max 20,000 characters; longer input rejected with a clear message |
| NFR-3 | Availability | Best effort, no uptime target (demo) |
| NFR-4 | Reliability | Each stage retries up to 3 times, then the job is marked FAILED with a clear error |
| NFR-5 | Security | Least-privilege IAM roles, no API keys in code, encryption at rest (AWS default), no login (demo only) |
| NFR-6 | Cost | A few dollars at most; investigate anything above about $5; run cdk destroy after demo |
| NFR-7 | Scale | One user at a time is enough |
| NFR-8 | Testability | Lambdas pass local tests (pytest) and cdk synth before the first deploy |

## Planned Stack (to confirm in Decide)

- Python for Lambdas (boto3, Bedrock converse) and CDK
- Single index.html with plain JavaScript

## Open Questions

- None
