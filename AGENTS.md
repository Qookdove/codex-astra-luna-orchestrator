# Codex project instructions

For substantial coding work, use the `astra-orchestrator` skill when its trigger conditions match.

The root owns architecture, decomposition, integration, verification, and acceptance.
Named subagent roles define behavior only; choose the child model and reasoning effort dynamically from live capability metadata and task risk.

Prefer bounded delegation with explicit scope and `fork_turns: none` when independent work materially improves delivery.
Do not delegate trivial work merely for parallelism.
Do not let multiple implementation agents edit the same files without explicit ownership boundaries.
Do not treat role-level `sandbox_mode` text as proof of runtime permission isolation; verify actual permissions when that matters.

User instructions always take precedence over this orchestration policy.
