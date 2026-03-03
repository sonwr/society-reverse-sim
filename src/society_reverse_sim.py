#!/usr/bin/env python3
"""Minimal forward + inverse social simulation utilities."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from typing import Iterable


@dataclass(frozen=True)
class ScenarioParams:
  population: int
  initial_adopters: int
  adopt_rate: float
  churn_rate: float
  steps: int


def _next_adopters(current: int, population: int, adopt_rate: float, churn_rate: float) -> int:
  gross_adopt = round((population - current) * adopt_rate)
  gross_churn = round(current * churn_rate)
  updated = current + gross_adopt - gross_churn
  return max(0, min(population, updated))


def _summarize_timeline(timeline: list[int], population: int) -> dict[str, object]:
  if not timeline:
    return {
      "peak_adopters": 0,
      "peak_step": 0,
      "net_change": 0,
      "saturation_ratio": 0.0,
      "stagnation_steps": [],
    }

  peak_adopters = max(timeline)
  peak_step = timeline.index(peak_adopters)
  net_change = timeline[-1] - timeline[0]
  saturation_ratio = round(timeline[-1] / population, 3) if population > 0 else 0.0
  stagnation_steps = [idx for idx in range(1, len(timeline)) if timeline[idx] == timeline[idx - 1]]

  return {
    "peak_adopters": peak_adopters,
    "peak_step": peak_step,
    "net_change": net_change,
    "saturation_ratio": saturation_ratio,
    "stagnation_steps": stagnation_steps,
  }


def simulate_forward(params: ScenarioParams) -> dict[str, object]:
  if params.population <= 0:
    raise ValueError("population must be positive")
  if not 0 <= params.initial_adopters <= params.population:
    raise ValueError("initial_adopters must be in [0, population]")
  if params.steps < 0:
    raise ValueError("steps must be non-negative")
  if not 0 <= params.adopt_rate <= 1:
    raise ValueError("adopt_rate must be in [0, 1]")
  if not 0 <= params.churn_rate <= 1:
    raise ValueError("churn_rate must be in [0, 1]")

  timeline = [params.initial_adopters]
  current = params.initial_adopters
  for _ in range(params.steps):
    current = _next_adopters(current, params.population, params.adopt_rate, params.churn_rate)
    timeline.append(current)

  return {
    "timeline": timeline,
    "final_adopters": timeline[-1],
    "summary": _summarize_timeline(timeline, params.population),
  }


def rank_inverse_candidates(
  observed_final_adopters: int,
  *,
  population: int,
  initial_adopters: int,
  steps: int,
  top_k: int = 5,
  rate_grid: Iterable[float] | None = None,
) -> list[dict[str, object]]:
  if not 0 <= observed_final_adopters <= population:
    raise ValueError("observed_final_adopters must be in [0, population]")
  if top_k <= 0:
    raise ValueError("top_k must be positive")

  if rate_grid is None:
    rate_grid = [i / 20 for i in range(11)]  # 0.00 to 0.50

  candidates: list[dict[str, object]] = []
  for adopt_rate in rate_grid:
    for churn_rate in rate_grid:
      params = ScenarioParams(
        population=population,
        initial_adopters=initial_adopters,
        adopt_rate=adopt_rate,
        churn_rate=churn_rate,
        steps=steps,
      )
      result = simulate_forward(params)
      error = abs(result["final_adopters"] - observed_final_adopters)
      fit_score = round(1 - (error / max(1, population)), 4)
      fit_band = "strong" if fit_score >= 0.9 else "moderate" if fit_score >= 0.75 else "weak"
      candidates.append(
        {
          "params": asdict(params),
          "predicted_final_adopters": result["final_adopters"],
          "abs_error": error,
          "fit_score": fit_score,
          "fit_band": fit_band,
        }
      )

  return sorted(
    candidates,
    key=lambda item: (
      item["abs_error"],
      -item["fit_score"],
      item["params"]["churn_rate"],
      -item["params"]["adopt_rate"],
    ),
  )[:top_k]


def _build_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(description="Forward + inverse social simulation.")
  subparsers = parser.add_subparsers(dest="command", required=True)

  forward = subparsers.add_parser("forward", help="Run forward simulation.")
  forward.add_argument("--population", type=int, required=True)
  forward.add_argument("--initial-adopters", type=int, required=True)
  forward.add_argument("--adopt-rate", type=float, required=True)
  forward.add_argument("--churn-rate", type=float, required=True)
  forward.add_argument("--steps", type=int, required=True)

  inverse = subparsers.add_parser("inverse", help="Rank inverse candidates by fit.")
  inverse.add_argument("--observed-final-adopters", type=int, required=True)
  inverse.add_argument("--population", type=int, required=True)
  inverse.add_argument("--initial-adopters", type=int, required=True)
  inverse.add_argument("--steps", type=int, required=True)
  inverse.add_argument("--top-k", type=int, default=5)

  return parser


def main() -> None:
  parser = _build_parser()
  args = parser.parse_args()

  if args.command == "forward":
    output = simulate_forward(
      ScenarioParams(
        population=args.population,
        initial_adopters=args.initial_adopters,
        adopt_rate=args.adopt_rate,
        churn_rate=args.churn_rate,
        steps=args.steps,
      )
    )
  else:
    output = rank_inverse_candidates(
      args.observed_final_adopters,
      population=args.population,
      initial_adopters=args.initial_adopters,
      steps=args.steps,
      top_k=args.top_k,
    )

  print(json.dumps(output, indent=2))


if __name__ == "__main__":
  main()
