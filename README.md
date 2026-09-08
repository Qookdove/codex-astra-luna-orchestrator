# Codex Hybrid Astra Orchestrator

A project-scoped Codex orchestration setup that keeps the root agent responsible for architecture and acceptance while dynamically routing bounded subagent work to the cheapest capable model.

The integration combines the original Astra/Luna orchestrator's installer, role contracts, concurrency controls, and rollout telemetry with Astra Advisor-style capability routing, explicit context-fork control, fresh review, and evidence-based cost reporting.

## Topology

```text
                 root architect
             (Astra on Pro profile)
                       |
              capability preflight
                       |
              delegation ROI gate
                       |
          +------------+------------+
          |            |            |
        Luna         Terra          Sol
      narrow /      explore /     difficult /
      repetitive     research       high-risk
          |            |            |
          +------------+------------+
                       |
            bounded behavior role
        explorer / worker / tester /
           researcher / reviewer
                       |
              integrate + verify
                       |
                fresh reviewer
                       |
           ship | fix-first | rethink
                       |
                  root accepts
```

Named roles define behavior only. The orchestration skill selects the child model and reasoning effort dynamically from task risk and live Codex capabilities.

## Why this structure

- preserves a strong root architecture/acceptance layer
- avoids forcing every child onto Luna
- avoids copying the entire parent history into every child by default
- retains bounded role contracts and one-writer-per-scope discipline
- keeps a hard concurrency ceiling
- separates real ChatGPT/Codex rate-limit telemetry from API-equivalent price scenarios
- uses a fresh review context before accepting substantial changes

See [`guides/hybrid-routing.md`](guides/hybrid-routing.md) for the integration design and routing policy.

## Layout

```text
.
├── .codex/
│   ├── config.toml          # Pro: Astra root
│   ├── config.plus.toml     # Plus compatibility: Luna max root
│   └── agents/
│       ├── explorer.toml
│       ├── worker.toml
│       ├── tester.toml
│       ├── reviewer.toml
│       └── researcher.toml
├── .agents/
│   └── skills/
│       └── astra-orchestrator/
│           └── SKILL.md
├── guides/
│   ├── hybrid-routing.md
│   ├── token-usage.md
│   └── ...
├── pricing/
│   └── 2026-09-04.json
├── scripts/
│   ├── token_usage.py
│   └── api_equivalent_cost.py
├── AGENTS.md
├── setup.sh
├── setup.ps1
└── LICENSE
```

## Root profiles

### Pro

```toml
model = "gpt-6-astra"
model_reasoning_effort = "low"

[agents]
enabled = true
max_concurrent_threads_per_session = 4
default_subagent_model = "gpt-5.6-luna"
default_subagent_reasoning_effort = "medium"
```

The subagent defaults are fallbacks only. The skill normally requests an explicit model and effort for each bounded delegation.

### Plus compatibility profile

```toml
model = "gpt-5.6-luna"
model_reasoning_effort = "max"
```

This keeps the long-lived root thread on Luna to reduce rate-limit pressure. It is not Astra-root orchestration and must not be described as such.

## Role vs model

Role and model are deliberately independent.

Examples:

- `explorer` + Terra for repository mapping
- `worker` + Luna for a narrow, well-specified edit
- `worker` + Sol for difficult cross-component debugging
- `tester` + Luna for targeted deterministic checks
- `reviewer` + Sol or another live-supported model for a fresh independent review

The role TOMLs do not pin model, reasoning effort, or sandbox mode. Current Codex role layers preserve parent permissions, so a role instruction such as "do not edit" is a behavior contract rather than proof of OS-level read-only isolation.

## Context policy

Native multi-agent V2 delegation should use:

```text
fork_turns: "none"
```

by default and pass only the bounded context needed for the task. Use recent-turn or full-history forks only when the child genuinely needs that conversation state.

## Routing guidance

- **Luna**: narrow, repetitive, low-risk, clear acceptance criteria
- **Terra**: exploration, large-context inspection, research, dependency/config tracing
- **Sol**: difficult implementation, ambiguous debugging, architecture-sensitive bounded work, high-value review
- **Astra**: preferred Pro root architect/acceptance owner; use as a child only when live capabilities expose it and the risk justifies it

Live tool metadata is authoritative. Never silently substitute a model/effort or claim a runtime pin that was not observed.

## Review lifecycle

For substantial implementation:

1. parent inspects the complete accumulated diff
2. parent reruns the highest-value requested checks
3. a fresh reviewer receives the actual change set and evidence
4. reviewer returns `ship`, `fix-first`, or `rethink`
5. `fix-first` requires correction, re-verification, and a fresh review
6. `rethink` requires a revised plan
7. root performs final acceptance

## Project setup

Clone this repository, then run the installer against a different target repository.

### macOS / Linux

```bash
./setup.sh
```

### Windows PowerShell

```powershell
powershell -ExecutionPolicy Bypass -File .\setup.ps1
```

or with PowerShell 7:

```powershell
pwsh -File .\setup.ps1
```

The installer asks for the target repository and plan, then offers to install:

- `.codex` — root configuration and behavioral roles
- `.agents` — orchestration skill
- `AGENTS.md` — project-level orchestration policy
- `scripts` — rollout telemetry and API-equivalent cost tools
- `pricing` — versioned pricing snapshot used by the cost tool

Existing files are listed before overwrite and updates default to `No`.

Project-scoped `.codex` configuration is loaded only for trusted projects.

## Personal/global setup

For global agent roles, copy the TOML files to:

```text
~/.codex/agents/
```

For the skill:

```text
~/.agents/skills/astra-orchestrator/
```

Merge the desired root profile into `~/.codex/config.toml`. Do not blindly overwrite existing MCP servers, providers, permissions, or other settings.

For telemetry and the API-equivalent scenario in a manually configured project, also copy `scripts/` and `pricing/` to that project root. The skill's documented commands use those project-relative paths.

## Using the skill

Codex may select the skill automatically for substantial work, or invoke it explicitly:

```text
$astra-orchestrator

Implement the invoice export endpoint.
Inspect the existing path first, route only bounded independent work,
verify the full diff, and obtain a fresh review before acceptance.
```

## Actual usage telemetry

Codex rollout files under `~/.codex/sessions` can be aggregated with:

```bash
scripts/token_usage.py --list --date 2026-09-07
scripts/token_usage.py --latest --date 2026-09-07
scripts/token_usage.py --latest --format json > usage.json
```

The report separates uncached input, cached input, output, reasoning tokens, thread/model usage, wall time, and recorded 5-hour / 7-day rate-limit deltas.

Raw token totals are not equivalent to plan consumption. Cached input can dominate, and the subscription rate-limit percentage is the better account-facing signal when available.

## API-equivalent cost scenario

Using a `token_usage.py` JSON report:

```bash
scripts/api_equivalent_cost.py usage.json
```

This applies the versioned pricing snapshot under `pricing/` and reports:

- routed API-equivalent estimate
- the same observed tokens repriced entirely at Astra
- same-token price difference

This is **not** ChatGPT subscription billing, usage credits, measured net savings, or evidence that an all-Astra run would consume the same tokens. Re-verify pricing before using historical rates as current estimates.

## Cost discipline

Orchestration is not free. The root remains alive for the full task, and each child has its own context. Therefore:

- do not orchestrate trivial work
- keep the default concurrency ceiling conservative
- prefer `fork_turns: none`
- keep child reports concise
- route only work with clear bounded ownership
- measure representative tasks before increasing parallelism

See [`guides/token-usage.md`](guides/token-usage.md) and [`guides/hybrid-routing.md`](guides/hybrid-routing.md).

## License

Licensed under the Apache License 2.0.
