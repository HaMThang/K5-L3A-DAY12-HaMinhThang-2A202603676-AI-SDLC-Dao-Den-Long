"""Test Contract v1.0 JSONL command line runner."""
import argparse
import json
import math
import sys
from pathlib import Path
from .game import Game


def parse_inputs(value):
    if not isinstance(value, dict) or set(value) != {"frames"} or not isinstance(value["frames"], list):
        raise ValueError("inputs must contain frames array")
    previous = -1
    frames = {}
    for frame in value["frames"]:
        if not isinstance(frame, dict) or set(frame) - {"tick", "move", "cam_yaw_deg", "jump", "interact", "pulse", "dash"}:
            raise ValueError("invalid frame")
        tick = frame.get("tick")
        if type(tick) is not int or tick <= previous or tick < 0:
            raise ValueError("frame ticks must increase strictly")
        previous = tick
        if "move" in frame:
            m = frame["move"]
            if not isinstance(m, list) or len(m) != 2 or any(type(x) not in (int, float) or not math.isfinite(x) or x < -1 or x > 1 for x in m):
                raise ValueError("invalid move")
        if "cam_yaw_deg" in frame and (type(frame["cam_yaw_deg"]) not in (int, float) or not math.isfinite(frame["cam_yaw_deg"])):
            raise ValueError("invalid cam yaw")
        for key in ("jump", "interact", "pulse", "dash"):
            if key in frame and type(frame[key]) is not bool: raise ValueError("invalid button")
        frames[tick] = frame
    return frames


def run(args):
    scenario = json.loads(Path(args.scenario).read_text(encoding="utf-8")) if args.scenario else None
    frames = parse_inputs(json.loads(Path(args.inputs).read_text(encoding="utf-8"))) if args.inputs else {}
    game = Game(args.seed, scenario)
    controls = {"move": [0, 0], "cam_yaw_deg": 0, "jump": False, "interact": False, "pulse": False, "dash": False}
    previous = controls.copy()
    with open(args.out, "w", encoding="utf-8", newline="\n") as out:
        def write(record): out.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
        write(game.snapshot())
        for tick in range(args.ticks):
            controls.update(frames.get(tick, {}))
            controls.pop("tick", None)
            edges = {key: controls[key] and not previous[key] for key in ("jump", "interact", "pulse", "dash")}
            game.step(controls, edges)
            for event in game.events: write(event)
            if game.tick % args.snapshot_every == 0 or game.state != "playing": write(game.snapshot())
            previous = {**controls}
            if game.state != "playing": break
        write({"type": "end", "ticks": game.tick, "state": game.state, "score": game.score})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--night", type=int, required=True)
    parser.add_argument("--scenario")
    parser.add_argument("--inputs")
    parser.add_argument("--ticks", type=int, required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--snapshot-every", type=int, default=10)
    args = parser.parse_args()
    if args.night != 1 or args.ticks < 0 or args.snapshot_every <= 0:
        parser.error("night must be 1 and ticks/snapshot-every must be valid")
    try:
        run(args)
    except (ValueError, KeyError, TypeError, json.JSONDecodeError, OSError) as exc:
        print(f"Invalid scenario/inputs/output: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__": sys.exit(main())
