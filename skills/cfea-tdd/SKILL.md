---
name: cfea-tdd
description: Run the Layer 3 Red-Green TDD loop from an approved Layer 2 contract — write unit tests encoding the contract in tests/, confirm they fail for the right reason (Red), then write implementation in src/ until they pass (Green) without touching tests/ during Green. Use after a contract in .specs/contracts/ is approved, or when asked to implement a feature under CFEA. Does not pause for human review — Layer 3 is AI-owned — but hands off to cfea-mutate rather than declaring done on green alone.
---

# CFEA — Layer 3: Internal Mutation Loop (Red-Green half)

Turn an approved contract into disposable code nobody has to read. The only
thing that makes that safe is that tests are written and locked *before*
implementation exists to satisfy them — write them the other order and they
just document whatever the code happens to do.

## Step 0 — check the input is ready

Only run against a contract that's been through `cfea-contract` and approved.
If there's no approved contract for this boundary, stop and send it back —
writing tests against an unapproved or missing contract means testing against
a moving target.

## Step 1 — Red

Write unit tests in `tests/` that encode the contract: every request/response
shape, status/exit code, and error case from the contract's traceability
mapping gets a corresponding test, not just the happy path.

Run the test harness and confirm every new test **fails**. Check *why* each
one fails — a failure because the behavior doesn't exist yet is Red; a failure
because of a typo, import error, or malformed test is not proof of anything.
Fix broken tests before treating the loop as validly Red.

Record the Red result (harness output, timestamp, or commit) as the baseline
for Step 4's check.

## Step 2 — lock tests/

Once Red is confirmed, `tests/` is frozen until Green is reached. This skill's
job is to *not* edit `tests/` from here on — but don't rely on your own
discipline for this. Write `.cfea/state.json`:

```json
{ "phase": "green", "locked_paths": ["tests/"], "since": "<git-sha-or-timestamp>" }
```

The `cfea-test-lock` hook (PreToolUse) reads this file and mechanically
blocks any Edit/Write under a locked path while `phase` is `"green"` — so the
rule is enforced outside the agent, not just followed by it. If that hook
isn't installed in this repo, say so before proceeding — running Layer 3
without it means the "tests aren't fake" guarantee rests entirely on trust.

## Step 3 — Green

Write and iterate on implementation code in `src/` only, until every test from
Step 1 passes. If a test turns out to be wrong or ambiguous, that is not a
license to edit it — stop, exit Green, and report which test and why. Silently
loosening a test to make it pass is the exact failure mode this whole
architecture exists to prevent.

Cap Green at **5 implementation attempts** against an unchanged test set. If
still red after 5, stop and report which tests are failing and what's been
tried — don't keep burning cycles on something the agent can't figure out.

## Step 4 — verify the loop was legitimate

Before declaring Green, diff `tests/` against the Step 1 baseline. It must be
byte-identical. If it isn't — whether from a hook miss or a gap in this
skill's own behavior — treat this as a failed run, not a pass: report it, do
not proceed.

## Step 5 — hand off

Green on an unchanged test set is necessary but not sufficient — it only
proves the tests as written pass, not that the tests are any good. Update
`.cfea/state.json` to `"phase": "mutate"` (or delete it) so the lock lifts —
`cfea-mutate` needs to edit `tests/` next. Hand off to `cfea-mutate`; do not
report this feature as done on Green alone.
