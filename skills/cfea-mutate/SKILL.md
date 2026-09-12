---
name: cfea-mutate
description: Run the Layer 3 mutation audit (Stryker/mutmut or equivalent) against code that just reached Green under cfea-tdd, scoped to new/changed files only. Strengthens tests until surviving mutants are killed or documented as equivalent, capped at 5 rounds. Use immediately after cfea-tdd hands off, before cfea-verify. This is the proof that tests aren't fake — Green alone only proves tests pass, not that they'd catch anything.
---

# CFEA — Layer 3: Internal Mutation Loop (Mutation half)

Green proves the tests pass. It doesn't prove they'd fail if the code were
wrong. Mutation testing is the actual proof: inject small faults, confirm the
tests catch them. This is what lets a human trust tests they never read.

Checklist:
1. Confirm Green + read the pinned mutation config (Step 0)
2. Scope to changed files, run full regression suite unmutated (Step 1)
3. Run the mutation tool (Step 2)
4. Triage each survivor: strengthen a test, or document as equivalent (Step 3)
5. Re-run suite + mutation tool after each round (Step 4)
6. Stop at 5 rounds if still unresolved (Step 5)
7. Record mutation_rounds and hand off to cfea-verify (Step 6)

## Step 0 — check the input is ready

Only run after `cfea-tdd` reports Green on an unchanged test set. Unlike that
skill, editing `tests/` here is expected and correct — the test lock from
Step 2 of `cfea-tdd` applies to the Red→Green loop, not to this phase.

Read `.specs/cfea.config.yaml` for the approved mutation framework and
command (see `cfea-bootstrap`). If it's missing or unapproved, stop — do not
pick a mutation tool yourself, and never hand-roll mutations by editing code
and eyeballing whether a test catches it. That's exactly the non-determinism
this layer exists to eliminate.

## Step 1 — scope

Mutate only files that are new or changed for this feature (diff against the
base branch/last known-good state). Do not re-mutate untouched code — its
existing tests already proved themselves in a prior pass. Instead, run the
**full existing regression suite** (not just this feature's tests) once,
unmutated, to catch breakage in code that depends on what just changed. That
full-suite run is regression safety; mutation is reserved for what's new.

## Step 2 — run the mutation tool

Run the framework/command pinned in `.specs/cfea.config.yaml` against the
scoped files. Record the mutation score and the list of surviving mutants.

## Step 3 — triage survivors

For each surviving mutant, default assumption is that it's **meaningful** — a
real behavioral change your tests should have caught but didn't. Add or
strengthen an assertion that would fail against that specific mutant, tied to
actual contract/spec behavior, not written just to defeat the mutant
mechanically.

Only mark a mutant **equivalent** (no observable output difference is
possible, so no test could ever kill it) if you can state concretely why —
and log that reasoning inline next to the mutant in your run summary. This is
a judgment call happening without a human in the loop, so the reasoning has to
be auditable after the fact, not just asserted.

- **Correctly equivalent:** a mutant changes `i++` to `i += 1` in a loop
  counter. No input produces a different output between the two — mark it
  equivalent and move on.
- **Not equivalent, don't mark it that way:** a mutant flips a boundary check
  from `>` to `>=`. That changes behavior at exactly one input value even if
  no current test happens to probe that value — it's a real gap, not an
  equivalent mutant. Add the assertion that exercises the boundary instead of
  writing it off.

Never resolve a survivor by weakening what a test checks, deleting a case, or
changing `src/` purely to dodge the mutant rather than to fix a real gap. The
goal is stronger proof, not a cleaner scorecard.

## Step 4 — re-verify each round

After each round of test changes: re-run the full changed-code test suite
(must stay Green) and re-run the mutation tool. Repeat Step 3 only on mutants
still surviving.

## Step 5 — cap at 5 rounds

If mutants still survive after **5 rounds**, stop. Report the surviving
mutants, what was tried each round, and why it didn't converge. Don't keep
spending cycles on a mutant the loop can't crack — that's a signal for a
human, not something to brute-force indefinitely.

## Step 6 — hand off

Once the mutation score is 100% (killed or explicitly documented equivalent),
record `"mutation_rounds": N` (how many rounds it took, 1–5) in
`.cfea/state.json` next to the `green_attempts`/`failure_log` fields
`cfea-tdd` already left there — `cfea-verify` rolls all of it into the final
receipt as trust signals, not just a binary pass. Hand off to `cfea-verify`.
No human pause needed unless Step 5's cap was hit.
