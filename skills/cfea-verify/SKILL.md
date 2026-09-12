---
name: cfea-verify
description: Run the Layer 4 verification gauntlet — boot the real app against ephemeral infra (Testcontainers/equivalent from .specs/cfea.config.yaml), replay every scenario from the Layer 2 contract's traceability mapping as real calls, assert strictly on inputs/outputs/exit codes/DB schema state, check declared NFRs, and emit a signed execution receipt. Use immediately after cfea-mutate reports a clean mutation score. This is the artifact a human trusts instead of reading src/ — it must stay deterministic and boundary-only, never AI judgment calls on internal behavior.
---

# CFEA — Layer 4: The Verification Engine

This is the proof. Everything upstream (spec, contract, tests, mutation) was
either human-reviewed or mechanically checked — this layer is where the
actual running system gets held against the contract, for real, in a clean
environment. The output of this skill is the thing a human reads instead of
`src/`.

Checklist:
1. Confirm clean mutation score + read the pinned verify config (Step 0)
2. Spin up ephemeral infra (Step 1)
3. Boot the app, wait for readiness (Step 2)
4. Replay every contract scenario as a real call (Step 3)
5. Check declared NFRs (Step 4)
6. Assert boundary-only — no internal log/behavior inspection (Step 5)
7. Tear down, emit the receipt (Step 6)
8. On any failure, route back to cfea-tdd rather than patching here (Step 7)

## Step 0 — check the input is ready

Only run after `cfea-mutate` reports a clean mutation score (100% killed or
documented equivalent). Read `.specs/cfea.config.yaml`'s `verify` block
(infra tool, boot command, readiness check) from `cfea-bootstrap`. If it's
missing or unapproved, stop — don't improvise how to boot the app or what
counts as ready.

## Step 1 — spin up ephemeral infrastructure

Use the configured infra tool (Testcontainers or equivalent) to boot real,
throwaway instances of whatever the app depends on — database, message
broker, WireMock stand-ins for third-party APIs. Never point verification at
shared or persistent infra; a run that isn't starting from clean state isn't
deterministic.

## Step 2 — boot the app

Start the app per the config's boot command, pointed at the ephemeral
dependencies from Step 1. Wait for the configured readiness signal (health
endpoint, port-open check, log line) before sending it anything. A request
fired at a not-yet-ready app is a false failure, not a real one.

## Step 3 — replay the contract

Walk the Layer 2 contract's traceability mapping scenario by scenario. For
each one, make the real call (HTTP request, CLI invocation) against the
running app and assert against what the contract declared: response/output
shape, status/exit code, resulting DB schema state where applicable. Every
scenario that was mapped in `cfea-contract` gets exercised here — this is
where an unmapped or vague scenario would have silently escaped, which is why
that step refused to let one through.

## Step 4 — check declared NFRs

For any NFR/SDD constraint that applies to this boundary (latency, rate
limits, auth policy, etc.), run whatever check the contract declares — a
load-test tool for a latency budget, a scanner for a security rule. Which
specific tool does it is an implementation detail; what's non-negotiable is
that every declared NFR has *something* plugged in to check it. If one is
declared with no check configured, flag it — don't silently skip it and don't
let it pass by default.

## Step 5 — stay strictly at the boundary

Assert only on inputs, outputs, exit codes, and database schema state. Do
**not** parse or reason about internal application logs, internal function
behavior, or implementation details to decide pass/fail — that reintroduces
AI judgment into what's supposed to be a deterministic check. If the boundary
signals aren't enough to tell whether a scenario passed, that's a contract gap
to send back to `cfea-contract`, not something to resolve by looking inside.

## Step 6 — tear down and emit the receipt

Tear down all ephemeral infra regardless of outcome. Emit an execution
receipt — what was run, what passed/failed per scenario, the mutation score
carried over from `cfea-mutate`, and the NFR check results. Pull
`green_attempts`, `failure_log`, and `mutation_rounds` out of
`.cfea/state.json` into the receipt too: a feature that took 5 tries to go
Green and 4 rounds to kill mutants passed the same gates as one that took 1
and 1, but it's a weaker trust signal and a human skimming receipts should be
able to see that difference at a glance, not just a pass/fail. This receipt
is the human-facing deliverable; present it plainly rather than just
reporting "done."

## Step 7 — on failure, route back, don't patch here

If any scenario fails, do not attempt a silent fix at this layer. Report
exactly which scenario and what the boundary showed, and hand back to
`cfea-tdd` for that specific case. Layer 4 is a judge, not a fixer — patching
code to satisfy a failing verification run without going back through Red-
Green-Mutate would undo everything those layers were for.
