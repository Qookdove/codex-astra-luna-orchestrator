#!/usr/bin/env python3
"""Static/smoke verification for the hybrid orchestrator repository."""

from __future__ import annotations

import importlib.util
import json
import py_compile
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROLE_DIR = ROOT / ".codex" / "agents"
FORBIDDEN_ROLE_KEYS = {"model", "model_reasoning_effort", "sandbox_mode"}


def fail(message: str) -> None:
    raise AssertionError(message)


def parse_toml(path: Path) -> dict:
    with path.open("rb") as fh:
        return tomllib.load(fh)


def verify_configs() -> None:
    for name in ("config.toml", "config.plus.toml"):
        path = ROOT / ".codex" / name
        data = parse_toml(path)
        agents = data.get("agents") or {}
        if agents.get("enabled") is not True:
            fail(f"{path}: agents.enabled must be true")
        ceiling = agents.get("max_concurrent_threads_per_session")
        if not isinstance(ceiling, int) or ceiling < 1 or ceiling > 4:
            fail(f"{path}: concurrency ceiling must be in 1..4")
        if not agents.get("default_subagent_model"):
            fail(f"{path}: fallback default_subagent_model is required")


def verify_roles() -> None:
    expected = {"explorer", "worker", "tester", "reviewer", "researcher"}
    found = set()
    for path in ROLE_DIR.glob("*.toml"):
        data = parse_toml(path)
        name = data.get("name")
        if name:
            found.add(name)
        forbidden = FORBIDDEN_ROLE_KEYS.intersection(data)
        if forbidden:
            fail(f"{path}: role must be model/permission agnostic; found {sorted(forbidden)}")
        if not data.get("developer_instructions"):
            fail(f"{path}: developer_instructions missing")
    if found != expected:
        fail(f"role set mismatch: expected {sorted(expected)}, got {sorted(found)}")


def verify_skill_contract() -> None:
    text = (ROOT / ".agents" / "skills" / "astra-orchestrator" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    required = [
        'fork_turns: "none"',
        "GPT-5.6 Luna",
        "GPT-5.6 Terra",
        "GPT-5.6 Sol",
        "ship | fix-first | rethink",
        "token_usage.py",
    ]
    for needle in required:
        if needle not in text:
            fail(f"SKILL.md missing required integration contract: {needle}")


def verify_docs_and_installers() -> None:
    paths = [
        ROOT / "README.md",
        *sorted((ROOT / "guides").glob("*.md")),
        ROOT / "setup.sh",
        ROOT / "setup.ps1",
    ]
    stale = [
        "Execute with Luna",
        "GPT-5.6 Luna executes, GPT-6 Astra reviews",
        "Subagents keep their pinned models",
        "with Luna subagents",
    ]
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for needle in stale:
            if needle in text:
                fail(f"{path}: stale fixed-routing wording remains: {needle}")

    token_guide = (ROOT / "guides" / "token-usage.md").read_text(encoding="utf-8")
    root_only_selector = (
        "scripts/token_usage.py --root <root-session-id-or-unique-prefix> "
        "--format json > usage.json"
    )
    if root_only_selector not in token_guide:
        fail("guides/token-usage.md must document --root JSON selection for root-only baselines")

    installer_contracts = {
        ROOT / "setup.sh": "for component in .codex .agents AGENTS.md scripts pricing; do",
        ROOT / "setup.ps1": "foreach ($component in '.codex', '.agents', 'AGENTS.md', 'scripts', 'pricing')",
    }
    for path, needle in installer_contracts.items():
        text = path.read_text(encoding="utf-8")
        if needle not in text:
            fail(f"{path}: installer must package scripts and pricing with project setup")

    subprocess.run(["sh", "-n", str(ROOT / "setup.sh")], check=True)


def verify_installer_smoke() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        target = Path(temp_dir) / "target"
        target.mkdir()
        answers = f"{target}\n" + "\n" * 6
        result = subprocess.run(
            ["sh", str(ROOT / "setup.sh")],
            input=answers,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            fail(
                "setup.sh smoke install failed:\n"
                f"stdout:\n{result.stdout}\n"
                f"stderr:\n{result.stderr}"
            )

        required = [
            ".agents/skills/astra-orchestrator/SKILL.md",
            "scripts/token_usage.py",
            "scripts/api_equivalent_cost.py",
            "pricing/2026-09-04.json",
        ]
        for relative in required:
            if not (target / relative).is_file():
                fail(f"setup.sh did not install required dependency: {relative}")


def load_cost_module():
    path = ROOT / "scripts" / "api_equivalent_cost.py"
    spec = importlib.util.spec_from_file_location("api_equivalent_cost", path)
    if spec is None or spec.loader is None:
        fail("cannot load api_equivalent_cost.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_cost_smoke() -> None:
    pricing = json.loads((ROOT / "pricing" / "2026-09-04.json").read_text(encoding="utf-8"))
    report = {
        "root": "root",
        "threads": [
            {
                "counted": True,
                "per_model": {
                    "gpt-6-astra": {
                        "input_tokens": 100_000,
                        "cached_input_tokens": 90_000,
                        "output_tokens": 2_000,
                    }
                },
            },
            {
                "counted": True,
                "per_model": {
                    "gpt-5.6-luna": {
                        "input_tokens": 50_000,
                        "cached_input_tokens": 40_000,
                        "output_tokens": 1_000,
                    }
                },
            },
        ],
    }
    module = load_cost_module()
    result = module.calculate(report, pricing)
    if result["status"] != "scenario_estimate":
        fail("cost calculator did not produce scenario_estimate")
    if result["routed_api_equivalent_usd"] != "0.294000":
        fail(f"unexpected routed cost: {result['routed_api_equivalent_usd']}")
    if result["same_token_astra_usd"] != "0.480000":
        fail(f"unexpected Astra reprice: {result['same_token_astra_usd']}")

    invalid_metadata = (
        ("schema_version", 2),
        ("currency", "EUR"),
        ("unit", "per_thousand_tokens"),
    )
    for field, value in invalid_metadata:
        bad_pricing = dict(pricing)
        bad_pricing[field] = value
        try:
            module.calculate(report, bad_pricing)
        except ValueError:
            pass
        else:
            fail(f"cost calculator must fail closed on unsupported pricing {field}")

    bad = {
        "root": "root",
        "threads": [
            {
                "counted": True,
                "per_model": {
                    "unknown-model": {
                        "input_tokens": 1,
                        "cached_input_tokens": 0,
                        "output_tokens": 0,
                    }
                },
            }
        ],
    }
    try:
        module.calculate(bad, pricing)
    except ValueError:
        pass
    else:
        fail("cost calculator must fail closed on an unpriced observed model")


def verify_python_syntax() -> None:
    for path in (ROOT / "scripts").glob("*.py"):
        py_compile.compile(str(path), doraise=True)


def main() -> int:
    verify_configs()
    verify_roles()
    verify_skill_contract()
    verify_docs_and_installers()
    verify_installer_smoke()
    verify_python_syntax()
    verify_cost_smoke()
    print("hybrid orchestrator verification: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"hybrid orchestrator verification: FAIL: {exc}", file=sys.stderr)
        raise
