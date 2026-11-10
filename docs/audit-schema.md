# Audit Record Schema

| Field | Purpose |
|---|---|
| `event_id` | Unique decision identifier |
| `timestamp` | UTC record time |
| `scenario_step` | Progressive scenario inject |
| `actor` and `audience` | Who supplied and who would receive the content |
| `purpose` | Declared processing purpose |
| `input_fingerprint_sha256` | Reproducible identifier without raw child text |
| `input_classification` | Observable risk classes |
| `retrieved_sources` | Source ID title authority section and URL |
| `applied_controls` | Controls executed by the agent |
| `decision_summary` | Short reviewable rationale without private chain-of-thought |
| `action` | Allowed blocked notified or escalated outcome |
| `result` | Scenario pass or fail |

The schema intentionally excludes raw messages, credentials, model prompts, hidden reasoning, and real family identifiers.

