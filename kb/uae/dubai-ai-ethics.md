# Dubai AI Ethics Principles and Guidelines

## Relevance to the use case

Dubai's AI ethics guidance emphasizes fairness, accountability, transparency, explainability, security, and human benefit. It also supports traceability of system failures and access to explanations for decisions that materially affect people.

## Controls implemented in the demo

- Every scenario step produces a structured audit event.
- The event names the sources, controls, action, and result.
- The audit record excludes raw child messages and private model reasoning.
- Uncertain child-safety decisions fail closed rather than guessing.

