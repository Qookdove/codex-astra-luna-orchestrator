# Token Usage

Orchestration has no single fixed token cost. Usage depends on repository size, task shape, child count, context-fork policy, model routing, and cache behavior.

Use the rollout telemetry Codex already writes under `~/.codex/sessions` instead of estimating from prompt size.

## What `token_usage.py` measures

`scripts/token_usage.py` groups root and subagent rollout files by root `session_id` and reports, when available:

- thread role and model
- reasoning effort recorded for the turn
- uncached input
- cached input
- output and reasoning-output tokens
- wall time
- 5-hour and 7-day rate-limit `used_percent`

```bash
scripts/token_usage.py --list --date 2026-09-07
scripts/token_usage.py --latest --date 2026-09-07
scripts/token_usage.py --latest --format json > usage.json
```

`--latest` intentionally selects the most recent session that spawned at least one non-guardian subagent, so it cannot select the recommended root-only baseline. For a root-only run, use `--list` to identify the root session id, then select that session explicitly:

```bash
scripts/token_usage.py --root <root-session-id-or-unique-prefix> --format json > usage.json
```

Add `--date YYYY-MM-DD` to the `--root` command when you want to limit the scan.

Raw `total_tokens` can be misleading because cached input may dominate. For ChatGPT Plus/Pro operation, the observable 5-hour and 7-day rate-limit deltas are the more useful account-facing signals when present.

## Hybrid-routing measurement protocol

Use the same prompt and repository state for each configuration.

Recommended cells:

1. root-only baseline
2. hybrid orchestrator with `fork_turns: none`
3. optional alternative route or concurrency setting

Representative tasks:

- localized fix
- multi-file feature
- cross-component bug
- research-heavy change

Record:

- task success and corrections required
- child models/efforts actually observed, when metadata exposes them
- subagent count
- uncached input / cached input / output
- wall time
- 5-hour and 7-day deltas
- reviewer verdict and material findings

Repeat important cells more than once. Agent runs have enough variance that a single run should not become a permanent routing rule.

## Context-fork effect

The hybrid skill defaults native multi-agent V2 children to:

```text
fork_turns: "none"
```

This prevents automatic full-history duplication and instead sends a bounded task contract. If a child requires recent conversational context, test a positive recent-turn count separately. Use full history only when it materially improves correctness.

## Historical fixed-topology sample

The following sample predates hybrid routing. It is retained only as a scale reference for why routing and context discipline matter.

- Task: cross-component file-watcher bug in a small TypeScript desktop app
- Legacy topology: Astra low root, three Luna medium execution threads, Astra low reviewer
- Wall time: 13m49s
- 5-hour window: 0% -> 66%
- 7-day window: 31% -> 42%
- total reported tokens: ~9.3M
- uncached input: ~340k
- input cache hit rate: 96.3%

Even with a very high cache-hit rate, the long-lived root and several child contexts consumed a large share of the 5-hour window. This is the main reason the hybrid design does not delegate mechanically and avoids full-history forks by default.

Do **not** use this legacy run as a prediction for the hybrid configuration.

## API-equivalent scenario

After generating `usage.json`:

```bash
scripts/api_equivalent_cost.py usage.json
```

The price script applies a versioned historical API pricing snapshot and reports:

- routed API-equivalent estimate
- the same observed tokens repriced at Astra
- same-token price difference

This is deliberately separate from the subscription-facing telemetry above.

It does **not** measure:

- ChatGPT subscription billing
- usage-credit consumption
- actual net savings
- what an all-Astra run would really consume
- quality or latency improvement

Different models can consume different numbers of tokens, and aggregated rollout data cannot prove every call's pricing tier or context-length eligibility. Re-verify current pricing before using the historical snapshot for current-cost decisions.

## Reading routed runs

A lower-priced child is useful only when it does not create enough retries, supervision, or follow-up work to erase the saving.

A practical routing decision should therefore consider both:

```text
quality / retries / wall time
            +
rate-limit delta / token telemetry / API-equivalent scenario
```

not model price alone.

## Reducing usage

In rough order of impact:

- keep trivial work root-only
- use `fork_turns: none` for bounded children
- avoid duplicate parent/child implementation
- keep child reports concise
- keep the concurrency ceiling low unless work is genuinely independent
- use Luna for clear narrow tasks
- use Terra for exploration/context-heavy reading
- reserve Sol/Astra-level effort for tasks whose risk or ambiguity justifies it
- skip fresh review only when the change is genuinely low-risk and independent review would add little value

See `hybrid-routing.md` for the full routing and review contract.
