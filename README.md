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
├── AGENTS.md
├── setup.sh
├── setup.ps1
└── LICENSE
```

## Main configuration knobs

Edit `.codex/config.toml`:

```toml
model = "gpt-6-astra"
model_reasoning_effort = "low"

[agents]
enabled = true
max_concurrent_threads_per_session = 4
default_subagent_model = "gpt-5.6-luna"
default_subagent_reasoning_effort = "medium"
```

Each role file is explicitly pinned to its intended model: Luna for explorer, worker, tester, and researcher; Astra for reviewer. This means changing only `default_subagent_model` will affect generic spawned agents, but not the named roles.

If you want one knob to control all subagents, remove the `model` and `model_reasoning_effort` overrides from each `.codex/agents/*.toml` file.

Then the named roles inherit the `[agents]` defaults.

## Project setup

Clone this repository:

```bash
git clone https://github.com/donvito/codex-astra-luna-orchestrator.git
cd codex-astra-luna-orchestrator
```

The target project must already exist and must be different from this setup
repository.

### macOS and Linux

Run the shell installer:

```bash
./setup.sh
```

### Windows

Run the PowerShell installer from Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup.ps1
```

With PowerShell 7, you can use:

```powershell
pwsh -File .\setup.ps1
```

### Installer prompts

When asked for the target repository, enter its absolute or relative path. For
example:

```text
Target repository path: ../my-project
```

The installer then asks whether to install each component:

- `.codex` contains the root configuration and agent role profiles.
- `.agents` contains the `astra-orchestrator` skill.
- `AGENTS.md` gives Codex the project-level orchestration instructions.

Press Enter or answer `y` to install a component; answer `n` to skip it. All
three components are selected by default.

If a component already exists, the installer lists the exact paths that would
be overwritten and asks again before making changes:

```text
WARNING: the following existing files will be overwritten:
  - .codex/config.toml
Update .codex? New files will be added; only paths listed above will be replaced. [y/N]
```

Existing-file updates default to `n`. If approved, missing files are added and
only the listed paths are replaced. Other files already present in the target
component remain untouched.

After setup, launch Codex from the target repository. Project-scoped `.codex`
configuration is loaded only for trusted projects.

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

## License

Licensed under the [Apache License 2.0](LICENSE).
