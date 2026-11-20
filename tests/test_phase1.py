import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from src.game import Game, T

ROOT = Path(__file__).resolve().parents[1]
STILL = {"move": [0, 0], "cam_yaw_deg": 0}


class PhaseOneTests(unittest.TestCase):
    def test_pickup_radius_and_capacity(self):
        g = Game(scenario={"random_motes": False, "random_shades": False,
                           "motes": [[T["pickup_radius"], 0, 0], [T["pickup_radius"] + .001, 0, 0]]})
        g.step(STILL, {})
        self.assertEqual(g.player["carried"], 1)
        self.assertEqual([e["name"] for e in g.events], ["mote_picked"])
        self.assertEqual(len(g.motes), 1)

    def test_deposit_lights_and_wins_without_scenario_score(self):
        g = Game(scenario={"random_motes": False, "random_shades": False,
                           "player": {"carried": T["lantern_cost"]},
                           "lanterns": [{"id": "L1", "pos": [0, 0, 0]}] +
                                       [{"id": f"L{i}", "lit": True} for i in range(2, 6)]})
        self.assertEqual(g.score, 0)
        g.step(STILL, {"interact": True})
        self.assertEqual(g.state, "won")
        self.assertEqual([e["name"] for e in g.events], ["deposit", "lantern_lit", "game_over"])
        self.assertEqual(g.player["carried"], 0)

    def test_pulse_stuns_and_pushes(self):
        g = Game(scenario={"random_motes": False, "random_shades": False,
                           "player": {"carried": T["pulse_cost"]}, "shades": [{"pos": [2, 0, 0]}]})
        g.step(STILL, {"pulse": True})
        self.assertEqual(g.player["carried"], 0)
        self.assertAlmostEqual(g.shades[0]["pos"][0], 2 + T["pulse_push_m"] / 15)
        self.assertEqual(g.snapshot()["shades"][0]["state"], "stunned")
        self.assertEqual(g.events[0]["data"], {"stunned_ids": ["S1"]})

    def test_hit_invulnerability_and_dawn(self):
        g = Game(scenario={"random_motes": False, "random_shades": False,
                           "shades": [{"pos": [0, 0, 0]}], "player": {"carried": 3}})
        g.step(STILL, {})
        self.assertEqual(g.player["flames"], 2)
        self.assertEqual(g.events[0]["data"]["dropped"], 1)
        for _ in range(30): g.step(STILL, {})
        self.assertEqual(g.player["flames"], 2)
        dawn = Game(scenario={"random_motes": False, "random_shades": False, "time_left_s": 1 / 60})
        dawn.step(STILL, {})
        self.assertEqual(dawn.events[-1]["data"]["reason"], "dawn")

    def test_camera_relative_move_and_jump(self):
        g = Game(scenario={"random_motes": False, "random_shades": False})
        g.step({"move": [0, 1], "cam_yaw_deg": 90}, {"jump": True})
        self.assertAlmostEqual(g.player["pos"][0], T["player_speed"] / 60)
        self.assertAlmostEqual(g.player["pos"][2], 0)
        self.assertGreater(g.player["pos"][1], 0)

    def test_interact_outside_radius_and_no_flames(self):
        g = Game(scenario={"random_motes": False, "random_shades": False,
                           "player": {"carried": 3},
                           "lanterns": [{"id": "L1", "pos": [T["interact_radius"] + .001, 0, 0]}]})
        g.step(STILL, {"interact": True})
        self.assertFalse(g.lanterns[0]["lit"])
        self.assertEqual(g.player["carried"], 3)
        hit = Game(scenario={"random_motes": False, "random_shades": False,
                             "player": {"flames": 1}, "shades": [{"pos": [0, 0, 0]}]})
        hit.step(STILL, {})
        self.assertEqual(hit.state, "lost")
        self.assertEqual(hit.events[-1]["data"], {"result": "lost", "reason": "no_flames"})

    def test_cli_determinism_and_bad_input(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            sc = d / "scenario.json"
            sc.write_text(json.dumps({"random_motes": False, "random_shades": False,
                                      "motes": [[0, 0, 0]]}), encoding="utf-8")
            outputs = []
            for name in ("a.jsonl", "b.jsonl"):
                out = d / name
                result = subprocess.run([sys.executable, "-m", "src.headless", "--seed", "7", "--night", "1",
                                         "--scenario", str(sc), "--ticks", "12", "--out", str(out)], cwd=ROOT, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                outputs.append(out.read_bytes())
            self.assertEqual(outputs[0], outputs[1])
            records = [json.loads(line) for line in outputs[0].splitlines()]
            self.assertEqual(records[0]["tick"], 0)
            self.assertEqual(records[-1], {"type": "end", "ticks": 12, "state": "playing", "score": 0})
            sc.write_text("{invalid", encoding="utf-8")
            bad = subprocess.run([sys.executable, "-m", "src.headless", "--seed", "7", "--night", "1",
                                  "--scenario", str(sc), "--ticks", "1", "--out", str(d / "bad.jsonl")], cwd=ROOT, capture_output=True)
            self.assertEqual(bad.returncode, 2)


if __name__ == "__main__": unittest.main()
