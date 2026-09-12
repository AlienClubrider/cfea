---
name: cfea-spec
description: Draft or update a Layer 1 CFEA specification (BDD Gherkin feature file for business behavior, or SDD markdown for technical tasks/NFRs) from a feature request, ask, or bug report. Use when starting new work under the Contract-First Engine Architecture, or when asked to create/update files under .specs/features/ or .specs/technical/. Drafts only — Layer 1 is human-owned, so this skill stops after drafting and hands back for human approval. Does not generate the Layer 2 interface contract (separate skill).
---

# CFEA — Layer 1: Human Intent

Produce the human-owned specification that everything downstream (contract, tests,
code, verification) is derived from and judged against. This is the only layer
where a human's judgment is the check — get it right here or nothing after it
can be trusted.

## Step 1 — classify the ask

Business-facing behavior (a feature, a user-visible flow, a bug in behavior) → **BDD**.
Non-functional or purely technical (latency budget, auth policy, retry behavior,
a refactor's invariants) → **SDD**.

If it's ambiguous, ask the user rather than guessing — this file is the thing a
human is going to review, so the type has to be right before drafting.

## Step 2 — gather intent

Do not invent acceptance criteria. Pull them from what the user actually said,
existing specs, or a codebase's current observed behavior for a bootstrap case.
If a scenario is missing a concrete input/output/edge case, ask — a vague
Given/When/Then produces a vague contract in the next skill, and vague contracts
are exactly what let an agent satisfy the letter of a spec while missing the intent.

**Probe for fake criteria.** For each acceptance criterion the user gives, ask
yourself: could a wrong or trivial implementation still satisfy this literally?
If yes, it's vacuous — not a spec, just words that sound like one. Drill in with
a Socratic follow-up (a concrete "what should happen if..." or "how would you
tell it apart from a version that just returns X?") until the criterion is
falsifiable — a specific input paired with a specific, checkable outcome.

Cap this at **5 drill-down rounds per scenario**. If it's still vague after 5,
stop drilling, write the scenario with what you have, and flag it explicitly
in your summary back to the user as unresolved/needs-their-input — don't loop
forever chasing precision the user hasn't got yet.

## Step 3 — write the artifact

**Business feature** → `.specs/features/<feature-slug>.feature`, standard Gherkin:

```gherkin
Feature: <name>
  <one-line business purpose>

  Scenario: <specific case>
    Given <concrete precondition>
    When <concrete action>
    Then <concrete, checkable outcome>
```

Write one scenario per distinct behavior/edge case, not one giant scenario.
Each scenario must be independently checkable — no "and also verify it's fast"
buried in a functional scenario. That belongs in an SDD NFR file instead.

**Technical/NFR** → `.specs/technical/<topic-slug>.md`:

```markdown
# <Topic>

## Rule
<the concrete, testable requirement — a number, a policy, an invariant>

## Applies to
<which feature(s)/contract(s)/endpoints this constrains>

## Rationale
<why this exists, if not obvious>
```

Every NFR rule must be phrased so a machine check could pass/fail it (a
threshold, a boolean policy, an enumerable list) — "should be fast" is not a
spec, "p99 < 200ms under 100 concurrent requests" is.

## Step 4 — stop for review

Do not proceed to contract generation. Present the drafted file(s) and a short
summary of what's in them, then stop and wait for explicit human approval or
edits. Layer 1 is human-owned by design — this skill's job ends at a reviewable
draft, not a merged spec.
