# Fast Iteration

Choose this preset when latency matters and you want a fast Astra root while
bounded subagents are routed dynamically by capability.

Add or merge this into:

`~/.codex/config.toml`

```toml
model = "gpt-6-astra"
model_reasoning_effort = "medium"
service_tier = "fast"
```

If your Codex version does not support `service_tier`, remove that line and
keep the model and reasoning settings.
