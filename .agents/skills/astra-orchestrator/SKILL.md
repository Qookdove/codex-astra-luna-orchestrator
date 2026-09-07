---
name: astra-orchestrator
description: Orchestrate substantial Codex work with a root architect, dynamically routed Sol/Terra/Luna subagents, bounded role contracts, fresh review, and measured verification. Use for multi-file features, cross-component debugging, repo-wide changes, research-heavy work, or explicit delegation. Do not use for trivial localized edits.
---

# Astra Orchestrator — hybrid routing

The user's explicit instructions take precedence over this skill.

## Goal

Preserve the original orchestrator's strengths — project-scoped configuration, bounded roles, concurrency limits, installer compatibility, and token telemetry — while using dynamic capability routing instead of hard-wiring every subagent to one model.

The parent session owns:

1. intent and constraints
2. architecture and decomposition
3. delegation decisions
4. model/effort routing
5. integration
6. parent-side verification
7. acceptance

Named agent roles define **behavior**, not model choice. Do not assume a role TOML pins model, reasoning effort, or sandbox permissions.

## Parent modes

- Pro profile: GPT-6 Astra is the preferred root architect.
- Plus profile: the configured Luna root is a compatibility/degraded-cost profile; do not falsely claim Astra root orchestration.
- Never change the parent model or effort from inside the skill.
- If runtime metadata exposes the parent model/effort, report what is observed. If it does not, say `unobservable` rather than inventing confirmation.

## Capability preflight

Before substantive delegation:

1. inspect the live `spawn_agent` / collaboration schema if available
2. determine which model and reasoning controls are actually exposed
3. treat live tool metadata as authoritative over this document
4. fail a model-pinned delegation closed if the selected model/effort cannot be requested safely
5. continue safe parent work when delegation is unavailable

Do not fabricate tools, models, effort levels, runtime confirmation, or permission isolation.

## Delegation gate

Classify the work as `root-only` or `delegated`.

Prefer root-only when the task is small, localized, sequential, or cheaper to finish directly than to create another context.

Delegate when a bounded independent deliverable materially improves at least one of:

- parallel progress
- context isolation
- repository exploration
- research quality
- implementation ownership
- independent verification
- review quality

Do **not** delegate merely because a task touches multiple files. Orchestration has context and rate-limit cost.

When the user explicitly asks for agents/subagents/parallelism, use real delegation if the live tool supports it.

## Dynamic model routing

Select the cheapest model that is likely to complete the bounded task without creating enough retries, supervision, or quality risk to erase the saving.

Use this as routing guidance, not a fixed role-to-model table:

### GPT-5.6 Luna

Prefer for:
- narrow, well-specified edits
- repetitive or mechanical implementation
- targeted test execution
- simple extraction or lookup
- low-risk bounded tasks with clear acceptance criteria

Typical effort: `low` or `medium`.

### GPT-5.6 Terra

Prefer for:
- repository exploration
- large-file or large-context inspection
- dependency/configuration tracing
- documentation and evidence gathering
- moderately ambiguous analysis where reading dominates writing

Typical effort: `medium` or `high`.

### GPT-5.6 Sol

Prefer for:
- difficult implementation
- cross-component debugging
- ambiguous technical reasoning
- risky refactors with bounded ownership
- architecture-sensitive implementation below the parent level
- high-value independent review when Astra subagent use is unavailable or unnecessary

Typical effort: `high` or above only when the live model supports it and task risk justifies it.

### GPT-6 Astra

Keep Astra primarily at the root on the Pro profile. A fresh Astra reviewer may be used when the live tool supports it and review risk justifies the extra cost, but never assume it is available as a child.

Escalate only after evidence: task ambiguity, failed lower-tier attempt, safety/security risk, architectural uncertainty, or high-cost failure potential.

## Role selection

Use named roles for bounded behavior contracts:

- `explorer`: map repository/data/control flow; no edits
- `researcher`: verify external/version-specific facts; no application-code edits
- `worker`: bounded implementation
- `tester`: reproduction and targeted verification; edit tests only when explicitly delegated
- `reviewer`: fresh-context review; no edits

Model and effort are selected independently from the role.

## Delegation contract

Every delegated task should specify:

- **Objective**: one concrete outcome
- **Scope**: exact files/module/subsystem/question when known
- **Context**: only what is needed to succeed
- **Constraints**: what must not change
- **Deliverable**: what to return or implement
- **Acceptance criteria**: how success will be checked

Prefer one writer per file or subsystem.

If the task expands into architecture, public API/schema changes, a new dependency, security-sensitive behavior, or another worker's ownership, stop expanding scope and return the decision to the parent.

## Context policy

For native multi-agent V2 delegation, prefer:

`fork_turns: "none"`

and pass the bounded context explicitly in the delegation contract.

Use a positive recent-turn count only when recent conversational state is genuinely necessary. Use `fork_turns: "all"` only when the child truly requires the entire parent conversation.

Rationale: full-history forks duplicate parent context into each child and can materially increase usage.

## Spawn contract

When the live tool supports these controls, each delegation should request:

- descriptive `task_name`
- `agent_type` for the behavior role
- explicit `model`
- explicit `reasoning_effort`
- `fork_turns: "none"` by default
- a bounded message containing the delegation contract

Requested values are not proof of realized runtime values. If runtime metadata exposes actual model/effort, keep requested and observed values separate. If unobservable, say so.

## Parallelism

Run independent work in parallel; serialize dependent work.

Good:
1. explorer maps backend
2. researcher verifies external API behavior
3. explorer maps frontend
4. parent synthesizes
5. bounded implementation
6. verification

Do not:
- spawn multiple writers for the same files without explicit ownership boundaries
- duplicate the same implementation in parent and child
- exceed the configured concurrency ceiling merely because more subtasks exist

The repository default ceiling is intentionally conservative. Raise it only after measuring the actual workload.

## Default substantial-work flow

1. capability preflight
2. inspect repository and classify risk
3. decide root-only vs delegated
4. if useful, spawn bounded exploration/research in parallel
5. parent chooses architecture and integration boundary
6. route implementation tasks dynamically
7. parent inspects accumulated changes
8. run/re-run the highest-value requested checks
9. start a **fresh** reviewer context when review is materially useful
10. resolve verdict
11. final verification and concise report

Do not spawn every role mechanically.

## Fresh review protocol

For substantial implementation, the parent must inspect the complete accumulated diff and verification evidence before review.

The fresh reviewer must not edit files and returns:

```text
ASTRA REVIEW
VERDICT: ship | fix-first | rethink
REASON: <evidence-based reason>
FINDINGS: <precise findings or none>
RESIDUAL RISK: <remaining risk or none>
```

Interpretation:

- `ship`: reviewer found no material blocker; parent may accept after its own checks
- `fix-first`: correct the issue, re-run verification, then obtain a fresh review
- `rethink`: architecture or assumptions are materially wrong; revise the plan before continuing

A reviewer verdict never replaces parent acceptance.

## Verification

Before claiming completion, the parent should verify the highest-value applicable checks:

- final diff inspection
- syntax/type checks
- targeted unit tests
- integration tests
- build success
- original reproduction path
- configuration compatibility
- unintended-change review

State any validation that could not be performed.

Do not make tests pass by hiding structural integration problems.

## Cost and context discipline

Keep parent context focused on:

- architecture decisions
- summarized evidence
- important diffs
- test results
- reviewer findings
- unresolved risks

Subagents should return concise conclusions, paths/symbols, commands, test results, and blockers instead of large raw logs.

Use `scripts/token_usage.py` after representative runs to measure:

- per-thread/model usage
- uncached vs cached input
- output/reasoning tokens
- wall time
- 5-hour and 7-day rate-limit deltas when recorded

If an API-equivalent price scenario is produced, label it separately from ChatGPT subscription usage. Same-token repricing is not evidence of actual all-Astra consumption or net subscription savings.

## Failure handling

If a subagent fails:

1. inspect the failure reason
2. retry only if the cause is transient or the contract can be narrowed
3. reroute model/effort only when evidence justifies escalation
4. do not silently ignore the failed delegation
5. do not claim success for work that was not verified

If spawning itself is unavailable, report the limitation and continue root-only when safe.

## User-facing reporting

Do not narrate every internal action unless the user requests orchestration visibility.

For substantial routed work, a compact route summary is enough:

```text
ROUTE
parent: <observed/unobservable model + effort>
delegation: <selected tasks/models/efforts or none>
risk: <short rationale>
```

Final answers should focus on:

- what changed
- what was verified
- material findings
- remaining risks/limitations
- measured usage only when available

Never claim a specific child model, effort, permission state, or delegation occurred unless runtime evidence supports that claim.
