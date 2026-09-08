#!/usr/bin/env python3
"""Estimate API-equivalent cost from token_usage.py JSON output.

This is a historical same-token pricing scenario, not ChatGPT subscription billing,
usage-credit consumption, or a measured all-Astra counterfactual.

Usage:
  scripts/api_equivalent_cost.py usage.json
  scripts/api_equivalent_cost.py usage.json --pricing pricing/2026-09-04.json
  scripts/token_usage.py --latest --format json > usage.json
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any

MILLION = Decimal(1_000_000)
SUPPORTED_PRICING_SCHEMA_VERSION = 1
SUPPORTED_PRICING_CURRENCY = "USD"
SUPPORTED_PRICING_UNIT = "per_million_tokens"


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as fh:
            obj = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc
    if not isinstance(obj, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return obj


def token_triplet(usage: dict[str, Any]) -> tuple[int, int, int]:
    try:
        total_input = int(usage.get("input_tokens") or 0)
        cached_input = int(usage.get("cached_input_tokens") or 0)
        output = int(usage.get("output_tokens") or 0)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid token count: {usage}") from exc
    if min(total_input, cached_input, output) < 0:
        raise ValueError("token counts must be non-negative")
    if cached_input > total_input:
        raise ValueError("cached_input_tokens cannot exceed input_tokens")
    return total_input - cached_input, cached_input, output


def money(tokens: int, rate: str | int | float | Decimal) -> Decimal:
    return Decimal(tokens) * Decimal(str(rate)) / MILLION


def model_cost(usage: dict[str, Any], rates: dict[str, Any]) -> Decimal:
    uncached, cached, output = token_triplet(usage)
    return (
        money(uncached, rates["input"])
        + money(cached, rates["cached_input"])
        + money(output, rates["output"])
    )


def merge_usage(target: dict[str, int], usage: dict[str, Any]) -> None:
    uncached, cached, output = token_triplet(usage)
    target["uncached_input_tokens"] += uncached
    target["cached_input_tokens"] += cached
    target["output_tokens"] += output


def q(value: Decimal) -> str:
    return str(value.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP))


def validate_pricing(pricing: dict[str, Any]) -> dict[str, Any]:
    schema_version = pricing.get("schema_version")
    if type(schema_version) is not int or schema_version != SUPPORTED_PRICING_SCHEMA_VERSION:
        raise ValueError(
            "unsupported pricing schema_version "
            f"{schema_version!r}; expected {SUPPORTED_PRICING_SCHEMA_VERSION}"
        )

    currency = pricing.get("currency")
    if currency != SUPPORTED_PRICING_CURRENCY:
        raise ValueError(
            f"unsupported pricing currency {currency!r}; expected {SUPPORTED_PRICING_CURRENCY!r}"
        )

    unit = pricing.get("unit")
    if unit != SUPPORTED_PRICING_UNIT:
        raise ValueError(
            f"unsupported pricing unit {unit!r}; expected {SUPPORTED_PRICING_UNIT!r}"
        )

    models = pricing.get("models")
    if not isinstance(models, dict) or "gpt-6-astra" not in models:
        raise ValueError("pricing snapshot must define models including gpt-6-astra")
    return models


def calculate(report: dict[str, Any], pricing: dict[str, Any]) -> dict[str, Any]:
    models = validate_pricing(pricing)

    threads = report.get("threads")
    if not isinstance(threads, list):
        raise ValueError("usage report must be token_usage.py JSON with a threads array")

    by_model: dict[str, dict[str, int]] = defaultdict(
        lambda: {
            "uncached_input_tokens": 0,
            "cached_input_tokens": 0,
            "output_tokens": 0,
        }
    )

    routed = Decimal("0")
    same_astra = Decimal("0")
    counted_threads = 0
    astra_rates = models["gpt-6-astra"]

    for thread in threads:
        if not isinstance(thread, dict) or thread.get("counted") is False:
            continue
        counted_threads += 1
        per_model = thread.get("per_model") or {}
        if not isinstance(per_model, dict):
            raise ValueError("thread per_model must be an object")
        for model, usage in per_model.items():
            if model not in models:
                raise ValueError(
                    f"pricing snapshot has no rate for observed model {model!r}; "
                    "refusing a partial routed-cost claim"
                )
            if not isinstance(usage, dict):
                raise ValueError(f"usage for {model} must be an object")
            merge_usage(by_model[model], usage)
            routed += model_cost(usage, models[model])
            same_astra += model_cost(usage, astra_rates)

    if counted_threads == 0:
        raise ValueError("usage report contains no counted threads")

    by_model_out: dict[str, Any] = {}
    for model, totals in sorted(by_model.items()):
        synthetic_usage = {
            "input_tokens": totals["uncached_input_tokens"] + totals["cached_input_tokens"],
            "cached_input_tokens": totals["cached_input_tokens"],
            "output_tokens": totals["output_tokens"],
        }
        by_model_out[model] = {
            **totals,
            "api_equivalent_usd": q(model_cost(synthetic_usage, models[model])),
        }

    difference = same_astra - routed
    difference_pct = (
        (difference / same_astra * Decimal(100)) if same_astra > 0 else Decimal(0)
    )

    return {
        "status": "scenario_estimate",
        "usage_source": "token_usage.py aggregated rollout JSON",
        "scope": "observed counted threads in the supplied session report",
        "pricing_snapshot_date": pricing.get("snapshot_date"),
        "pricing_eligibility_assumption": pricing.get("eligibility"),
        "routed_api_equivalent_usd": q(routed),
        "same_token_astra_usd": q(same_astra),
        "same_token_price_difference_usd": q(difference),
        "same_token_price_difference_percent": q(difference_pct),
        "by_model": by_model_out,
        "limits": [
            "Historical API-equivalent scenario only.",
            "Not ChatGPT subscription billing or usage-credit consumption.",
            "Not a measured all-Astra counterfactual: another model may consume different tokens.",
            "Aggregated rollout telemetry cannot prove per-call context-length or service-tier pricing eligibility.",
            "Re-verify pricing before using this as a current-cost estimate.",
        ],
    }


def render_md(result: dict[str, Any]) -> str:
    lines = [
        "### API-equivalent cost scenario",
        "",
        f"- pricing snapshot: `{result.get('pricing_snapshot_date')}`",
        f"- routed estimate: `${result['routed_api_equivalent_usd']}`",
        f"- same observed tokens repriced at Astra: `${result['same_token_astra_usd']}`",
        (
            "- same-token price difference: "
            f"${result['same_token_price_difference_usd']} "
            f"({result['same_token_price_difference_percent']}%)"
        ),
        "",
        "| Model | Uncached in | Cached in | Output | API-equivalent USD |",
        "|---|---:|---:|---:|---:|",
    ]
    for model, row in result["by_model"].items():
        lines.append(
            f"| {model} | {row['uncached_input_tokens']:,} | "
            f"{row['cached_input_tokens']:,} | {row['output_tokens']:,} | "
            f"${row['api_equivalent_usd']} |"
        )
    lines += ["", "Limits:"]
    lines.extend(f"- {item}" for item in result["limits"])
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("usage", type=Path, help="JSON output from scripts/token_usage.py --format json")
    parser.add_argument(
        "--pricing",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "pricing" / "2026-09-04.json",
    )
    parser.add_argument("--format", choices=("md", "json"), default="md")
    args = parser.parse_args(argv)

    try:
        result = calculate(load_json(args.usage), load_json(args.pricing))
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(render_md(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
