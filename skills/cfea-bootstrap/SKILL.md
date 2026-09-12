---
name: cfea-bootstrap
description: One-time (or stack-change-triggered) setup that detects a repo's language/stack and proposes the concrete deterministic tools CFEA runs on top of — mutation framework, test runner, ephemeral-infra/verification tool, boot command, linter — writing them to .specs/cfea.config.yaml. Use before any other CFEA skill runs in a repo that has no cfea.config.yaml yet, or when the stack has materially changed. Every other CFEA skill that needs to execute (not just instruct) reads this config and refuses to improvise if it's missing.
---

# CFEA — Bootstrap: pin the deterministic tools

Skills like `cfea-mutate` and `cfea-verify` are orchestration prose — they call
real tools to do the actual deterministic work (mutation, ephemeral infra).
They can't pick those tools themselves at run time; an agent improvising which
mutation framework to invoke, or hand-rolling mutations itself, is exactly the
non-determinism this architecture exists to eliminate. This skill exists to
make that choice once, explicitly, with a human's eyes on it.

## Step 1 — detect the stack

Identify language(s), package/build manager, and whatever test framework is
already in use. Prefer what's already present over introducing a second one —
if the repo already runs Jest, don't propose Vitest alongside it. Note if it's
a monorepo with multiple stacks; each may need its own config block.

## Step 2 — propose concrete tools

For each stack detected, propose:

- **Test runner** — existing one if present, otherwise the stack's standard.
- **Mutation framework** — e.g. Stryker (JS/TS), mutmut or cosmic-ray
  (Python), PIT (Java/Kotlin), cargo-mutants (Rust), go-mutesting/gremlins
  (Go). Pick one with real maintenance activity; don't propose an
  unmaintained tool just because it technically exists.
- **Verification/ephemeral infra** — Testcontainers' SDK for the language
  where one exists; fall back to a documented docker-compose-based approach
  where it doesn't. Include how the app under test gets **booted** (command)
  and how readiness is detected (health endpoint, port-open check, log line).
- **Linter/static analysis** — existing config if present, otherwise the
  stack's standard.

Don't guess silently on any of these — where there's a real choice (e.g. two
viable mutation frameworks), surface the tradeoff briefly and let the human
pick.

## Step 3 — flag uncovered legacy code

If there's existing `src/` code with no corresponding contract in
`.specs/contracts/` or tests in `tests/`, don't assume it's covered — flag it
explicitly. That code needs golden-master/characterization tests generated
from its current observed behavior before any CFEA refactor skill is allowed
to touch it. This skill only needs to flag the gap, not close it.

## Step 4 — scaffold structure

Ensure `.specs/features/`, `.specs/contracts/`, `.specs/technical/`, `src/`,
and `tests/` exist. Don't move or rename existing code to fit this shape —
if the repo's layout differs, record the actual paths in the config (Step 5)
instead of forcing a restructure.

## Step 5 — write config and stop for approval

Write everything from Steps 2–4 to `.specs/cfea.config.yaml`. Example shape:

```yaml
stack:
  language: typescript
test:
  runner: vitest
  command: npm test
mutation:
  framework: stryker
  command: npx stryker run --mutate <changed-files>
verify:
  infra: testcontainers-node
  boot_command: npm run start
  readiness: http://localhost:3000/health
lint:
  command: npm run lint
paths:
  specs: .specs/
  src: src/
  tests: tests/
```

Present the proposal and stop — do not let any other CFEA skill treat this
config as active until a human has approved it. Tool choice here is a trust
decision, same tier as spec and contract approval.

## Step 6 — re-run on drift

If the stack changes materially later (new language added, test runner
swapped, infra approach changed), re-run this skill rather than letting a
downstream skill silently work against a stale config.
