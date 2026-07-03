# Anti-Patterns

> Lessons from real multi-agent runs. Write-ups of what worked are common and
> cheap; these are the things **we got wrong** — the scarce material.

---

## AP1: A soft constraint is an ignored constraint

**Symptom**: "Should also create a README" sat in the soft-constraints
section; the first batch ended with no README anywhere.

**Root cause**: anything outside the hard-constraint list gets skipped by the
executor with high probability.

**Prevention**: promote critical artifacts (README / index / report) to hard
constraints, and give them their own self-check items.

---

## AP2: Executing on unverified inputs

**Symptom**: source paths / input data / preconditions written in the plan
didn't exist; the executor found out halfway through.

**Prevention**: verify every input (paths, data sources, declared counts)
with actual commands before the brief is finalized. The executor's first
action is a precheck. Trust command output, not the document's "should
exist".

---

## AP3: Surface identifiers instead of content-level verification

**Symptom**: deduplication by filename / ID / label copied over items with
identical content but different names; citation matching by title merged
different papers with the same title.

**Prevention**: after any bulk operation, run one content-level integrity
check (hash / record count / test pass rate). Never decide "same or
different" from names, titles, or IDs. Deduplication logic goes into the
self-check report with evidence.

---

## AP4: Documented constraints without enforcement gates

**Symptom**: the brief said "deviation > 20% must escalate"; at +30% the
executor decided to continue on its own. Result compliant, process violated.

**Root cause**: a documented constraint is not an enforcement gate. Nothing
in the execution loop said `if condition then halt`.

**Prevention**: make critical constraints executable — scripts or assertions
that abort on failure. **Rule: wherever the docs say "must", the execution
layer has a matching forced stop.**

---

## AP5: Held items get lost

**Symptom**: items marked "on hold" were nearly forgotten at final
acceptance.

**Prevention**: held items get their own section, never mixed into batch
lists; final acceptance explicitly checks their state ("not done" vs
"handed off"). Hold is not skip — every held item needs a continuation plan.

---

## AP6: The self-check report papers over problems

**Symptom**: a beautiful self-check report, six checks all PASS; the
reviewer's independent verification found real problems.

**Root cause**: agents write "I did X", not "I ran X and got Y". A report is
self-attestation, not proof.

**Prevention**: physically separate self-check from final review — the
executor attests, the reviewer independently falsifies. The cheapest
high-yield verification: re-run one count/integrity check yourself.

---

## AP7: Binary verdicts cause needless rework

**Symptom**: with only PASS/FAIL, every "direction right, details off" case
gets bounced for full rework.

**Prevention**: three-state verdicts (PASS / CONDITIONAL PASS / FAIL) plus
the four-way remediation classification (see SKILL.md). First ask "is the
target state right", then "was the process compliant".

---

## AP8: The reviewer does the executor's job

**Symptom**: the reviewer quietly fixes the executor's mistakes.

**Root cause**: it's faster in the moment — and guarantees the executor
makes the same mistake next time.

**Prevention**: reviewers take only zero-risk, fully-determined actions
(doc fixes, table updates, running verification commands). Anything needing
judgment or creation goes back to the executor. The reviewer's job is
finding problems, not fixing them.

---

## AP9: Foreground polling instead of a completion signal

**Symptom**: after dispatching a worker, the orchestrator sat in a foreground
loop re-reading status to guess "done yet?" — no structured completion
signal, the user watching a spinner, and the polling itself misfiring on
UI-idle heuristics.

**Root cause**: the dispatch mechanism was treated as an incidental step
rather than a first-class decision. Foreground polling costs the model
nothing — the cost lands on the user.

**Prevention**:
- Decide **how you will know it's done before you dispatch** — that choice is
  part of the dispatch, not an afterthought.
- Prefer your runtime's structured completion event (a done message, a task
  callback, an exit status) over screen-scraping status.
- If you must wait, wait in the background so completion wakes you; never a
  foreground tight loop.
- When polling turns flaky (misreads, repeated retries), that is itself the
  signal to switch mechanisms — stop and re-evaluate instead of retrying
  harder.

---

## Pre-flight checklist

| # | Check | Anti-pattern |
|---|-------|--------------|
| 1 | Critical artifacts in the hard-constraints section? | AP1 |
| 2 | Every input verified with real commands? | AP2 |
| 3 | Content-level integrity check planned after bulk ops? | AP3 |
| 4 | Critical thresholds backed by command-level forced stops? | AP4 |
| 5 | Held items in their own section, checked at final acceptance? | AP5 |
| 6 | Reviewer verifying independently, not just reading reports? | AP6 |
| 7 | Verdicts three-state? | AP7 |
| 8 | Reviewer/executor boundary explicit? | AP8 |
| 9 | Completion signal chosen before dispatch — no foreground polling? | AP9 |
