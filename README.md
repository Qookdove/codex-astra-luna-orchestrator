# Codex Astra Orchestrator + Luna Subagents

A configurable Codex setup where GPT-6 Astra is the root/orchestrator and reviewer, while GPT-5.6 Luna is the default and pinned model for execution subagents.

## Layout

```text
.
├── .codex/
│   ├── config.toml
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
└── AGENTS.md
```

## Main configuration knobs

Edit `.codex/config.toml`:

```toml
model = "gpt-6-astra"
model_reasoning_effort = "low"

[agents]
enabled = true
max_concurrent_threads_per_session = 6
default_subagent_model = "gpt-5.6-luna"
default_subagent_reasoning_effort = "max"
```

Each role file is explicitly pinned to its intended model: Luna for explorer, worker, tester, and researcher; Astra for reviewer. This means changing only `default_subagent_model` will affect generic spawned agents, but not the named roles.

If you want one knob to control all subagents, remove the `model` and `model_reasoning_effort` overrides from each `.codex/agents/*.toml` file.

Then the named roles inherit the `[agents]` defaults.

## Recommended install: project scoped

Copy all three project items into the root of your repository:

```bash
cp -R .codex /path/to/your/repo/
cp -R .agents /path/to/your/repo/
cp AGENTS.md /path/to/your/repo/AGENTS.md
```

Launch Codex from that repository.

Project-scoped `.codex` configuration is only loaded for trusted projects.

## Personal/global setup

For agents, copy the TOML files to:

```text
~/.codex/agents/
```

For the skill, copy the skill folder to:

```text
~/.agents/skills/astra-orchestrator/
```

Merge the settings from `.codex/config.toml` into your existing:

```text
~/.codex/config.toml
```

Do not blindly overwrite your existing global config if you already have MCP servers, providers, permissions, or other settings.

## Using the skill

Codex may select the skill automatically when the task matches its description.

You can also invoke it explicitly from Codex CLI or the IDE extension with:

```text
$astra-orchestrator
```

Example prompt:

```text
$astra-orchestrator

Implement the new invoice export endpoint.
Have explorer map the existing invoice/export path first.
Use workers for bounded implementation, tester for verification,
and reviewer for an independent final review.
```

## Suggested topology

```text
                 GPT-6 Astra
             root / orchestrator
                      |
      +---------------+---------------+
      |               |               |
   explorer          worker         researcher
     Luna             Luna             Luna
      |               |
      +-------+-------+
              |
           tester
            Luna
              |
          reviewer
           Astra
              |
              v
         GPT-6 Astra
      integrate + verify
```

## Tuning

For cheaper/faster runs:
- set Astra reasoning to `medium`
- set Luna reasoning to `low` or `medium`
- use 3-4 concurrent threads

For larger codebases:
- keep Astra at `high`
- keep Luna at `medium`
- use 6-8 concurrent threads, only when tasks are actually independent

For strict parent/child separation:
- keep explorer/reviewer/researcher read-only
- keep worker/tester workspace-write
- leave the root in workspace-write so it can integrate changes

## Important behavior

Explicit model choices during a spawn override `[agents]` defaults. Custom agent files that specify `model` or `model_reasoning_effort` also take precedence over inherited defaults.

The execution role files are pinned to Luna intentionally, while the reviewer is pinned to Astra for independent final review. Astra remains the orchestrator unless you deliberately change the role configuration.
