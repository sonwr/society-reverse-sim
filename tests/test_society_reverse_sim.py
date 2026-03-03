import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"

if str(SRC_DIR) not in sys.path:
  sys.path.insert(0, str(SRC_DIR))

from society_reverse_sim import ScenarioParams, rank_inverse_candidates, simulate_forward


class TestForwardSimulation(unittest.TestCase):
  def test_forward_timeline_is_deterministic_and_bounded(self):
    result = simulate_forward(
      ScenarioParams(
        population=100,
        initial_adopters=10,
        adopt_rate=0.2,
        churn_rate=0.05,
        steps=4,
      )
    )
    self.assertEqual(result["timeline"], [10, 28, 41, 51, 58])
    self.assertEqual(result["final_adopters"], 58)
    self.assertEqual(result["summary"]["peak_adopters"], 58)
    self.assertEqual(result["summary"]["peak_step"], 4)
    self.assertEqual(result["summary"]["net_change"], 48)
    self.assertEqual(result["summary"]["saturation_ratio"], 0.58)
    self.assertEqual(result["summary"]["stagnation_steps"], [])
    self.assertTrue(all(0 <= value <= 100 for value in result["timeline"]))

  def test_invalid_initial_adopters_raises(self):
    with self.assertRaises(ValueError):
      simulate_forward(
        ScenarioParams(
          population=10,
          initial_adopters=11,
          adopt_rate=0.1,
          churn_rate=0.1,
          steps=1,
        )
      )


class TestForwardSummary(unittest.TestCase):
  def test_summary_reports_stagnation_steps(self):
    result = simulate_forward(
      ScenarioParams(
        population=100,
        initial_adopters=50,
        adopt_rate=0.0,
        churn_rate=0.0,
        steps=3,
      )
    )
    self.assertEqual(result["timeline"], [50, 50, 50, 50])
    self.assertEqual(result["summary"]["stagnation_steps"], [1, 2, 3])


class TestInverseRanking(unittest.TestCase):
  def test_inverse_ranking_finds_exact_match(self):
    truth = ScenarioParams(
      population=80,
      initial_adopters=8,
      adopt_rate=0.2,
      churn_rate=0.05,
      steps=5,
    )
    observed_final = simulate_forward(truth)["final_adopters"]
    ranking = rank_inverse_candidates(
      observed_final,
      population=truth.population,
      initial_adopters=truth.initial_adopters,
      steps=truth.steps,
      top_k=3,
      rate_grid=[0.05, 0.1, 0.2, 0.3],
    )
    self.assertEqual(ranking[0]["abs_error"], 0)
    self.assertEqual(ranking[0]["params"]["adopt_rate"], 0.2)
    self.assertEqual(ranking[0]["params"]["churn_rate"], 0.05)


class TestCli(unittest.TestCase):
  def test_forward_cli_prints_json(self):
    proc = subprocess.run(
      [
        sys.executable,
        str(SRC_DIR / "society_reverse_sim.py"),
        "forward",
        "--population",
        "50",
        "--initial-adopters",
        "5",
        "--adopt-rate",
        "0.3",
        "--churn-rate",
        "0.1",
        "--steps",
        "3",
      ],
      check=True,
      capture_output=True,
      text=True,
    )
    payload = json.loads(proc.stdout)
    self.assertEqual(payload["timeline"], [5, 19, 26, 30])
    self.assertEqual(payload["final_adopters"], 30)


if __name__ == "__main__":
  unittest.main()
