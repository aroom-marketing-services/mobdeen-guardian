# Solution Architecture and ITU Mapping

## System boundary

Mobdeen Guardian is a standalone reference implementation. It receives synthetic family-learning requests and does not connect to Mobdeen production systems. The policy decision remains deterministic. An optional language model may draft wording only after the request is minimized and allowed.

## Processing flow

1. Intake records the actor, audience, declared purpose, scenario step, and synthetic context.
2. Preprocessing aliases family names, removes direct contact data, and classifies risk.
3. Retrieval searches a local 256-dimensional hashed bag-of-words index built from the manifest.
4. The policy layer applies guardian review, purpose limitation, best-interests, and escalation controls.
5. The optional generator receives minimized text and source context only for allowed requests.
6. Distribution packages the response, citations, controls, and action.
7. The sink is either a guardian-review response or a blocked-and-escalated outcome.
8. The audit logger writes an input fingerprint, source references, controls, action, and result.

## ITU T Y 3172 mapping

| Pipeline element | Mobdeen Guardian component | Evidence |
|---|---|---|
| SRC | Guardian child or system scenario input | `scenarios/child_safety_progressive.json` |
| C | `AgentRequest` intake | `src/mobdeen_guardian/models.py` |
| PP | Aliasing redaction and risk classification | `src/mobdeen_guardian/guardrails.py` |
| M | Local vector retrieval and optional text generator | `kb.py` and `generator.py` |
| P | Deterministic policy decision | `agent.py` |
| D | Response packaging with citations | `AgentResponse` |
| SINK | Guardian review or blocked escalation | `demo-output.json` |
| MLFO | Agent orchestration and provider selection | `MobdeenGuardianAgent` |
| Sandbox | Offline mode synthetic data and environment-only secrets | README and `.env.example` |
| Human supervision | Mandatory guardian review before child delivery | guardrail control and scenario results |

## Readiness mapping

| Dimension considered by the hackathon | Implementation |
|---|---|
| Open data and open-source management | Source register manifest hashes and Apache-2.0 code |
| Generative AI content ecosystem | Grounded output with an offline default and optional provider |
| Regional contextualization | Arabic family-learning use case and UAE policy sources |
| Domain integration | Education and family services |
| Human interaction and supervision | Guardian approval barrier before child delivery |
| Policy opportunity identification | Gap mapping with global examples |
| Social inclusion | Simple Arabic and offline operation |
| Infrastructure and energy | Small standard-library demo with no required cloud runtime |

## Auditability boundary

The audit record is designed for review without exposing private model chain-of-thought. It records the observable facts needed to reproduce a decision: input fingerprint, classification, retrieved sources, controls, summary, action, and result.

