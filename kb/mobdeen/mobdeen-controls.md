# Mobdeen Guardian Published Safety Controls

## Data controls

- Child names are replaced with aliases before retrieval or generation.
- Email, phone, URL, school, address, and location indicators trigger minimization or blocking.
- The audit log stores a SHA-256 input fingerprint, not raw child text.

## Decision controls

- A current guardian consent and review gate is required before child delivery.
- High-risk uses fail closed.
- Commercial targeting based on inferred child vulnerability is prohibited.
- Policy decisions are deterministic even when an optional language model drafts wording.

## Operational controls

- The reference implementation works offline with synthetic data.
- External generation is optional and uses environment variables only.
- The public package contains no production credentials, family data, billing code, or infrastructure configuration.
- Audit events identify sources, controls, action, and result without exposing private chain-of-thought.

