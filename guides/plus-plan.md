# Plus Plan Compatibility Profile

Choose this profile when you want orchestration but need the long-lived root thread to stay on Luna to reduce pressure on the 5-hour window.

The installers (`setup.sh`, `setup.ps1`) install `.codex/config.plus.toml` as the target repository's `.codex/config.toml` when you select `Plus`.

```toml
model = "gpt-5.6-luna"
model_reasoning_effort = "max"

[agents]
enabled = true
max_concurrent_threads_per_session = 4
default_subagent_model = "gpt-5.6-luna"
default_subagent_reasoning_effort = "medium"
```

This is a compatibility/cost profile, not Astra-root orchestration. Named role files remain model-agnostic. When the live Codex spawn tool exposes explicit model and effort controls, the skill may still route bounded children to Luna, Terra, or Sol according to task risk.

Do not assume an Astra reviewer is available on this profile. Reviewer behavior is fixed by the `reviewer` role, while its model is selected from live-supported capabilities and task risk.

Measure the actual result on your account with `scripts/token_usage.py`; do not infer plan consumption from raw token counts alone.
