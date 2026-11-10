# Mobdeen Guardian

Mobdeen Guardian is a policy-grounded AI agent for safe family learning. It helps a supervising parent create an age-appropriate weekly activity plan while minimizing child data, retrieving relevant policy controls, requiring guardian review, and producing an auditable decision record.

This repository is a standalone hackathon submission. It contains no production code, credentials, real family data, payment logic, or internal infrastructure configuration from Mobdeen.

## What the demonstration proves

- A searchable knowledge base built from official UAE, ITU, and global policy sources.
- Data minimization and child-name aliasing before any model call.
- Guardian consent and review gates.
- Progressive error scenarios with incomplete information.
- Source attribution and a reviewable audit record without private chain-of-thought.
- Fail-closed handling for child personal data and commercial targeting based on inferred vulnerability.

## Architecture

```text
Parent or child input
        |
        v
Data minimization and risk classification
        |
        v
Knowledge retrieval from local vector index
        |
        v
Policy controls and optional AI text generator
        |
        v
Guardian review gate
        |
        +----> Approved family guidance
        |
        +----> Block and escalate
        |
        v
Audit record with sources rules action and result
```

The pipeline maps to ITU-T Y.3172 as `SRC -> C -> PP -> M -> P -> D -> SINK`, with orchestration, sandboxing, and human supervision around the flow. See `docs/architecture.md` for the full mapping.

## Quick start

Python 3.11 or newer is sufficient. The default demonstration is fully offline and uses only the Python standard library.

### Windows PowerShell

```powershell
python ingestion/build_index.py
python demo/run_demo.py
python -m unittest discover -s tests -v
```

### macOS or Linux

```bash
python3 ingestion/build_index.py
python3 demo/run_demo.py
python3 -m unittest discover -s tests -v
```

The demonstration writes:

- `artifacts/demo-output.json`
- `artifacts/audit-log.jsonl`
- `artifacts/test-results.txt` when the packaged verification command is used

## Optional model provider

The judged demonstration does not require an external model. A pluggable OpenAI-compatible generator is included for teams that want to test generated wording after the deterministic policy decision.

```powershell
Copy-Item .env.example .env
# Set values locally. Never commit .env.
```

Only minimized text may be sent to a provider. Policy decisions remain deterministic and fail closed.

## Repository map

- `src/mobdeen_guardian/`: agent, retrieval, guardrails, generators, and audit logging.
- `kb/`: curated policy summaries and source manifest.
- `ingestion/`: deterministic local vector-index builder.
- `scenarios/`: progressive evaluation scenario and expected outcomes.
- `demo/`: synthetic family input and runner.
- `tests/`: retrieval, guardrail, and end-to-end scenario checks.
- `docs/`: architecture, gap mapping, source register, audit schema, and video script.
- `submission/`: technical report and handoff files for the submitting team.

## Safety and privacy

- Use synthetic data only.
- Never add credentials or real family records.
- Do not log raw child messages.
- Do not expose private model reasoning. The audit log records inputs by fingerprint, sources, applied controls, action, and result.
- This repository demonstrates technical and policy controls. It is not legal advice.

## License

Apache License 2.0. Third-party source documents remain under their original terms. The source register records provenance and reuse notes.

