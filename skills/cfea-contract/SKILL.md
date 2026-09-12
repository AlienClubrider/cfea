---
name: cfea-contract
description: Draft or update a Layer 2 CFEA interface contract (OpenAPI/Swagger YAML for APIs, flag/exit-code spec for CLIs) from an approved Layer 1 spec in .specs/features/ or .specs/technical/. Use after a spec has been reviewed and approved by a human, when asked to create/update files under .specs/contracts/, or before any implementation work starts on a feature. Drafts only — pauses for human approval before anything downstream (tests, code) can start, especially when the change touches an existing boundary.
---

# CFEA — Layer 2: Interface Contracts

Turn the human-owned spec into a machine-readable boundary that Layer 3/4 can
verify against. This is the piece every later stage trusts instead of reading
code — if it's loose or incomplete, everything downstream inherits that gap.

## Step 0 — check the input is ready

Only run against a spec that's been through `cfea-spec` and approved by a
human. If the spec still has scenarios flagged unresolved (drilled to the
5-round cap and left vague), stop — don't draft a contract around a criterion
nobody could pin down. Send it back for the human to resolve first.

## Step 1 — determine contract shape

HTTP/RPC service → OpenAPI (or equivalent schema for the protocol in use).
CLI/binary → a flag/argument/exit-code spec covering every invocable path.
Match whatever the spec's scenarios actually exercise — don't draft endpoints
or flags the spec never mentions.

## Step 2 — draft with full traceability

Every `Given/When/Then` in the spec must land somewhere concrete in the
contract: a request shape, a response shape, a status/exit code, an error
case. Walk the spec scenario by scenario and require each one to map to
something in the contract before moving to the next.

- Happy-path scenarios → success response/exit-code shape.
- Edge-case and error scenarios from the spec → explicit error responses/exit
  codes, not an implicit catch-all. If the spec described a failure mode, the
  contract must name it.
- NFR/SDD files that apply to this boundary (rate limits, auth, latency
  budgets) → encode as contract-level constraints where the format allows
  (e.g. OpenAPI security schemes, response headers), and note the rest as
  companion constraints Layer 4 must check even if the schema format can't
  express them directly.

If a spec scenario can't be mapped to anything concrete in the contract, that's
the same signal as a vacuous acceptance criterion in Layer 1 — stop and flag it
rather than papering over it with a generic shape.

## Step 3 — write the artifact

`.specs/contracts/<name>.yaml` (or `.md` for CLI specs without a natural
schema format). Include a short traceability block at the top mapping each
spec scenario to the contract element(s) it produced, so a human reviewer
doesn't have to reverse-engineer the mapping themselves.

## Step 4 — flag boundary changes explicitly

If this contract already exists, diff against the current version before
writing. A net-new contract is lower stakes than a change to a boundary other
code already depends on — call out anything that looks breaking (removed
field, narrowed type, changed status/exit code, tightened constraint) at the
top of your summary, not buried in the diff.

## Step 5 — stop for review

Do not proceed to `cfea-tdd`. Present the drafted/updated contract, the
traceability mapping, and any flagged gaps or breaking changes, then wait for
explicit human approval. This is the second and last human checkpoint in the
pipeline — everything after this point (tests, code, mutation audit,
verification) is judged against what gets approved here.
