# Full Hybrid Orchestration

Choose this preset when you want Astra to remain the Pro root architect while bounded subagent work is routed dynamically by capability.

```text
Astra root
  -> delegation ROI gate
  -> Luna / Terra / Sol selected per bounded task
  -> parent integration + verification
  -> fresh reviewer
  -> ship | fix-first | rethink
```

Root configuration:

```toml
model = "gpt-6-astra"
model_reasoning_effort = "medium"
service_tier = "fast"

[agents]
enabled = true
max_concurrent_threads_per_session = 4

# Fallback only; the skill normally requests child model/effort explicitly.
default_subagent_model = "gpt-5.6-luna"
default_subagent_reasoning_effort = "medium"
```

Do not pin `model`, `model_reasoning_effort`, or `sandbox_mode` inside named role TOMLs. Roles define behavior; the orchestration skill chooses the child model and effort from the live tool schema and task risk.

Default child context should use `fork_turns: "none"` and receive only the bounded context required for the delegated task.

If your Codex version does not support `service_tier`, remove that line and keep the model and reasoning settings.

See `hybrid-routing.md` for the routing and review policy.
