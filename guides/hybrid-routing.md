# Hybrid Astra orchestration

This repository composes two complementary ideas:

- the original Astra/Luna orchestrator provides project-scoped installation, behavioral agent roles, concurrency limits, and Codex rollout telemetry;
- Astra Advisor contributes dynamic capability routing, explicit context-fork control, runtime-evidence discipline, and a fresh-review acceptance loop.

The integration keeps those responsibilities separate instead of flattening them into one implementation.

## Final topology

```text
Root architect / acceptance owner
        |
        +-- capability preflight
        |
        +-- delegation ROI gate
        |
        +-- dynamic route
        |      |- Luna: narrow / repetitive / low-risk
        |      |- Terra: exploration / research / context-heavy
        |      `- Sol: difficult implementation / debugging / high-value review
        |
        +-- bounded behavior role
        |      |- explorer
        |      |- researcher
        |      |- worker
        |      |- tester
        |      `- reviewer
        |
        +-- integrate + parent verification
        |
        `-- fresh review -> ship | fix-first | rethink
```

On the Pro profile the preferred root is GPT-6 Astra. The Plus profile preserves the existing Luna-root compatibility option and must not be described as Astra-root orchestration.

## Responsibility split

### Preserve

- `setup.sh` and `setup.ps1`
- project-scoped `.codex` and `.agents` installation
- Pro and Plus root profiles
- five bounded behavioral roles
- hard concurrency ceiling
- `scripts/token_usage.py` and real 5-hour / 7-day telemetry when Codex records it
- public `$astra-orchestrator` invocation

### Compose

- root architecture + dynamic child routing
- behavioral role + independently selected model/effort
- rollout telemetry + API-equivalent price scenario
- parent verification + fresh reviewer verdict

### Adapt

- role files no longer pin model or reasoning effort; they only define behavior
- role files no longer claim sandbox isolation that the current Codex role layer does not enforce
- child context defaults to `fork_turns: none` in the orchestration contract
- fixed Luna execution becomes capability-based Luna/Terra/Sol routing

### Resolve

- fixed role-to-model mapping conflicted with explicit runtime model routing; runtime routing now owns model/effort selection
- mandatory delegation conflicted with orchestration overhead; a delegation ROI gate now decides whether another context is worthwhile
- reviewer model pinning conflicted with risk-based review; reviewer behavior is fixed while its model is selected from live capabilities

### Remove

- hard-coded model and reasoning lines from named role TOMLs
- role-level `sandbox_mode` claims that could be mistaken for an enforced child permission boundary
- the rule that every substantial/multi-file task must spawn a Luna child

No public project entry point is removed.

## Routing contract

Model choice and role choice are orthogonal.

Example:

```text
Task: trace a configuration bug across many files
role: explorer
model: Terra
reasoning: medium/high
fork_turns: none
```

```text
Task: apply a small, fully specified fix
role: worker
model: Luna
reasoning: low/medium
fork_turns: none
```

```text
Task: resolve an ambiguous cross-component concurrency defect
role: worker
model: Sol
reasoning: high+
fork_turns: none unless recent parent turns are genuinely required
```

Live tool metadata wins over these examples.

## Context policy

`fork_turns: none` is the default because every full-history child duplicates parent context. Pass the bounded task context explicitly.

Escalate to a positive recent-turn count only when the child needs conversation state that is expensive or error-prone to restate. Use `all` only when the entire parent history is materially required.

## Review contract

The parent first inspects the complete accumulated diff and reruns the highest-value checks. A fresh reviewer then returns:

```text
ASTRA REVIEW
VERDICT: ship | fix-first | rethink
REASON: ...
FINDINGS: ...
RESIDUAL RISK: ...
```

The reviewer does not edit files. `ship` is necessary but not sufficient: final acceptance remains with the parent.

## Usage measurement

Measure the subscription-facing behavior first:

```bash
scripts/token_usage.py --latest --format json > usage.json
```

This captures the observable rollout usage, cache share, wall time, and rate-limit deltas.

For a historical API-equivalent price scenario:

```bash
scripts/api_equivalent_cost.py usage.json
```

The second number is a same-token price scenario only. It is not ChatGPT billing, usage-credit consumption, or proof that an all-Astra run would have used the same number of tokens.

## Validation protocol

Before promoting a routing change, run the same representative tasks under at least two configurations:

1. root-only baseline
2. hybrid orchestration

Use a mix of:
- localized fix
- multi-file feature
- cross-component bug
- research-heavy task

Compare:
- completion quality
- retries/corrections
- wall time
- uncached/cached input
- output/reasoning tokens
- 5-hour and 7-day rate-limit deltas
- reviewer findings

A routing tier is useful only if lower cost or higher throughput is not erased by retries, supervision, or weaker results.

## Known limitations

- Current Codex capability schemas can change; model/effort support must be checked live.
- Named role behavior is an instruction contract, not proof of OS-level sandbox isolation.
- `token_usage.py` depends on rollout fields that can change between Codex versions.
- API-equivalent pricing is historical and must be re-verified for current estimates.
- The repository cannot prove end-to-end model routing without executing inside a Codex host that exposes native subagents.
