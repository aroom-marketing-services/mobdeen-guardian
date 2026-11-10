# Mobdeen Guardian Demonstration Video Script

Target length: five minutes. Official maximum: seven minutes.

## 0:00 to 0:30 Problem and solution

Show the title slide and say:

“Mobdeen Guardian helps a supervising parent create safe, age-appropriate family-learning guidance. The agent uses a policy knowledge base, minimizes child data, requires guardian review, and records an auditable decision.”

## 0:30 to 1:10 Hardware software and architecture

Show `docs/architecture.md` and the repository tree.

- Hardware: one laptop. No production mobile device or cloud account is required.
- Software: Python 3.11 or newer and this repository.
- Data: one synthetic family record.
- Explain the path: intake, minimization, retrieval, policy controls, optional generator, guardian gate, and audit event.

## 1:10 to 2:05 Step 1 normal guidance

Run:

```powershell
python ingestion/build_index.py
python demo/run_demo.py
```

Open step 1 in `artifacts/demo-output.json`.

- Expected: `ALLOW_WITH_GUARDIAN_REVIEW`.
- Actual: short Arabic plan for the guardian with policy sources.
- Point out that the plan is not delivered directly to the child.

## 2:05 to 3:05 Step 2 child personal data

Open step 2.

- The synthetic input contains a name, school, secrecy request, and phone number.
- Expected: block provider use, remove identifiers, provide a safe reply, and notify the guardian.
- Actual: `BLOCK_AND_NOTIFY_GUARDIAN`.
- Show that the audit record contains a fingerprint but not the phone number or raw message.

## 3:05 to 4:05 Step 3 commercial targeting

Open step 3.

- The system proposes a paid offer based on inferred child vulnerability.
- Expected and actual: `BLOCK_AND_ESCALATE`.
- Explain purpose limitation, best interests, and human policy review.
- Link the comparison to UNICEF, the UK Children's Code, COPPA, and the EU AI Act.

## 4:05 to 4:40 Auditability and ITU mapping

Show one line from `artifacts/audit-log.jsonl` and the table in `docs/architecture.md`.

Explain that the record contains sources, controls, the action, and result. It does not publish private chain-of-thought. Point to `SRC -> C -> PP -> M -> P -> D -> SINK`, the orchestrator, sandbox, and guardian supervision.

## 4:40 to 5:00 Gaps and close

Show `docs/gap-mapping.md`.

“The main gaps are guardian approval for generated child content, measurable Arabic age appropriateness, inferred child data, commercial targeting based on vulnerability, and human supervision as an enforceable delivery barrier. The repository is public, reproducible, and uses synthetic data only.”

End with the final GitHub URL after Shrouq creates the public repository.

