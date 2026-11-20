"""Deterministic 60 Hz game simulation, shared by browser and headless runner."""
import json
import math
import random
from pathlib import Path

T = json.loads((Path(__file__).resolve().parents[1] / "game.contract.json").read_text(encoding="utf-8"))["tuning"]
HZ = 60


def distance(a, b):
    return math.hypot(a[0] - b[0], a[2] - b[2])


def pos(value):
    if not isinstance(value, list) or len(value) != 3 or any(type(v) not in (int, float) or not math.isfinite(v) for v in value):
        raise ValueError("position must be a finite [x,y,z] array")
    return [float(v) for v in value]


class Game:
    def __init__(self, seed=0, scenario=None):
        scenario = scenario or {}
        if not isinstance(scenario, dict):
            raise ValueError("scenario must be an object")
        self.rng = random.Random(seed)
        self.tick = 0
        self.state = "playing"
        self.score = 0
        self.events = []
        self.player = {"pos": [0.0, 0.0, 0.0], "flames": T["flames"], "carried": 0}
        self.invuln_until = 0
        self.vertical_speed = 0.0
        self.pulse_ready = 0
        self.time_limit = T["night1_duration_s"]
        self.lanterns = [{"id": f"L{i+1}", "pos": [round(14 * math.sin(i * 2 * math.pi / 5), 3), 0.0, round(14 * math.cos(i * 2 * math.pi / 5), 3)], "lit": False, "deposited": 0} for i in range(5)]
        self.motes = [{"id": f"M{i+1}", "pos": [round(7 * math.sin(i * 2 * math.pi / 18), 3), 0.0, round(7 * math.cos(i * 2 * math.pi / 18), 3)]} for i in range(18)]
        self.shades = [{"id": "S1", "pos": [18.0, 0.0, 0.0], "stun_until": 0}]
        self.next_mote = 19
        self.next_shade = 2
        self.random_motes = True
        self.random_shades = True
        self.apply_scenario(scenario)

    def apply_scenario(self, s):
        allowed = {"player", "random_motes", "random_shades", "motes", "shades", "lanterns", "time_left_s"}
        if set(s) - allowed:
            raise ValueError("unknown scenario field")
        if "player" in s:
            p = s["player"]
            if not isinstance(p, dict) or set(p) - {"pos", "carried", "flames"}:
                raise ValueError("invalid player")
            if "pos" in p: self.player["pos"] = pos(p["pos"])
            for key in ("carried", "flames"):
                if key in p:
                    if type(p[key]) is not int or p[key] < 0: raise ValueError("invalid player value")
                    self.player[key] = p[key]
        for key in ("random_motes", "random_shades"):
            if key in s:
                if type(s[key]) is not bool: raise ValueError("invalid random flag")
                setattr(self, key, s[key])
        if s.get("random_motes") is False and "motes" not in s: self.motes = []
        if s.get("random_shades") is False and "shades" not in s: self.shades = []
        if "motes" in s:
            if not isinstance(s["motes"], list): raise ValueError("invalid motes")
            self.motes = [{"id": f"M{i+1}", "pos": pos(p)} for i, p in enumerate(s["motes"])]
            self.next_mote = len(self.motes) + 1
        if "shades" in s:
            if not isinstance(s["shades"], list): raise ValueError("invalid shades")
            self.shades = []
            for i, sh in enumerate(s["shades"]):
                if not isinstance(sh, dict) or set(sh) - {"id", "pos"} or "pos" not in sh: raise ValueError("invalid shade")
                self.shades.append({"id": sh.get("id", f"S{i+1}"), "pos": pos(sh["pos"]), "stun_until": 0})
            self.next_shade = len(self.shades) + 1
        if "lanterns" in s:
            if not isinstance(s["lanterns"], list): raise ValueError("invalid lanterns")
            seen = set()
            for patch in s["lanterns"]:
                if not isinstance(patch, dict) or set(patch) - {"id", "pos", "lit", "deposited"} or patch.get("id") not in {l["id"] for l in self.lanterns} or patch["id"] in seen: raise ValueError("invalid lantern")
                seen.add(patch["id"])
                l = next(l for l in self.lanterns if l["id"] == patch["id"])
                if "pos" in patch: l["pos"] = pos(patch["pos"])
                if "lit" in patch:
                    if type(patch["lit"]) is not bool: raise ValueError("invalid lit")
                    l["lit"] = patch["lit"]
                if "deposited" in patch:
                    if type(patch["deposited"]) is not int or patch["deposited"] < 0: raise ValueError("invalid deposited")
                    l["deposited"] = patch["deposited"]
        if "time_left_s" in s:
            v = s["time_left_s"]
            if type(v) not in (int, float) or not math.isfinite(v) or v < 0: raise ValueError("invalid time")
            self.time_limit = float(v)

    def emit(self, name, data):
        self.events.append({"type": "event", "tick": self.tick, "name": name, "data": data})

    def finish(self, state, reason):
        if self.state != "playing": return
        self.state = state
        if state == "won":
            self.score += max(0, int(self.time_left())) * T["score"]["per_second_left"] + self.player["flames"] * T["score"]["per_flame_left"]
        self.emit("game_over", {"result": state, "reason": reason})

    def time_left(self):
        return max(0.0, self.time_limit - self.tick / HZ)

    def step(self, controls, edges):
        if self.state != "playing": return
        self.events = []
        self.tick += 1
        p = self.player
        move = controls["move"]
        yaw = math.radians(controls["cam_yaw_deg"])
        dx = move[0] * math.cos(yaw) + move[1] * math.sin(yaw)
        dz = -move[0] * math.sin(yaw) + move[1] * math.cos(yaw)
        mag = math.hypot(dx, dz)
        if mag > 1: dx, dz = dx / mag, dz / mag
        p["pos"][0] += dx * T["player_speed"] / HZ
        p["pos"][2] += dz * T["player_speed"] / HZ
        if edges.get("jump") and p["pos"][1] <= 0:
            self.vertical_speed = 5.0
        if p["pos"][1] > 0 or self.vertical_speed > 0:
            p["pos"][1] = max(0.0, p["pos"][1] + self.vertical_speed / HZ)
            self.vertical_speed -= 12.0 / HZ
            if p["pos"][1] == 0: self.vertical_speed = 0.0
        # The shore blocks movement; falling is disabled in Phase 1.
        radius = math.hypot(p["pos"][0], p["pos"][2])
        if radius > 19.5:
            p["pos"][0] *= 19.5 / radius
            p["pos"][2] *= 19.5 / radius
        for mote in list(self.motes):
            if p["carried"] < T["carry_capacity"] and distance(p["pos"], mote["pos"]) <= T["pickup_radius"] + 1e-9:
                self.motes.remove(mote)
                p["carried"] += 1
                self.score += T["score"]["per_mote"]
                self.emit("mote_picked", {"carried": p["carried"]})
        if edges.get("interact"):
            candidates = [l for l in self.lanterns if not l["lit"] and distance(p["pos"], l["pos"]) <= T["interact_radius"] + 1e-9]
            if candidates:
                l = min(candidates, key=lambda x: distance(p["pos"], x["pos"]))
                amount = min(p["carried"], max(0, T["lantern_cost"] - l["deposited"]))
                if amount:
                    p["carried"] -= amount
                    l["deposited"] += amount
                    self.emit("deposit", {"lantern_id": l["id"], "amount": amount, "deposited": l["deposited"]})
                if l["deposited"] >= T["lantern_cost"]:
                    l["lit"] = True
                    self.score += T["score"]["per_lantern"]
                    self.emit("lantern_lit", {"lantern_id": l["id"]})
        if edges.get("pulse") and p["carried"] >= T["pulse_cost"] and self.tick >= self.pulse_ready:
            p["carried"] -= T["pulse_cost"]
            self.pulse_ready = self.tick + round(T["pulse_cooldown_s"] * HZ)
            stunned = []
            for sh in self.shades:
                if distance(p["pos"], sh["pos"]) <= T["pulse_radius"] + 1e-9:
                    stunned.append(sh["id"])
                    sh["stun_until"] = self.tick + round(T["pulse_stun_s"] * HZ)
                    vx, vz = sh["pos"][0] - p["pos"][0], sh["pos"][2] - p["pos"][2]
                    length = math.hypot(vx, vz) or 1
                    sh["pos"][0] += T["pulse_push_m"] * vx / length
                    sh["pos"][2] += T["pulse_push_m"] * vz / length
            self.score += len(stunned) * T["score"]["per_stun"]
            self.emit("pulse", {"stunned_ids": stunned})
        for sh in self.shades:
            if self.tick < sh["stun_until"]: continue
            # Lit lanterns make a circular safe zone that shades cannot enter.
            d = distance(p["pos"], sh["pos"])
            if d:
                step = min(d, T["shade_speed"] / HZ)
                candidate = [sh["pos"][0] + (p["pos"][0] - sh["pos"][0]) * step / d, 0, sh["pos"][2] + (p["pos"][2] - sh["pos"][2]) * step / d]
                if not any(l["lit"] and distance(candidate, l["pos"]) < T["safe_radius"] for l in self.lanterns):
                    sh["pos"] = candidate
            player_safe = any(l["lit"] and distance(p["pos"], l["pos"]) <= T["safe_radius"] for l in self.lanterns)
            if not player_safe and distance(p["pos"], sh["pos"]) <= T["shade_hit_radius"] + 1e-9 and self.tick >= self.invuln_until:
                p["flames"] = max(0, p["flames"] - 1)
                dropped = math.ceil(p["carried"] * T["hit_drop_ratio"])
                p["carried"] -= dropped
                self.invuln_until = self.tick + round(T["invuln_s"] * HZ)
                self.emit("player_hit", {"by": sh["id"], "flames": p["flames"], "dropped": dropped})
        if all(l["lit"] for l in self.lanterns): self.finish("won", "all_lit")
        elif p["flames"] <= 0: self.finish("lost", "no_flames")
        elif self.time_left() <= 0: self.finish("lost", "dawn")

    def snapshot(self):
        def rounded(v): return round(v, 3)
        return {"type": "snapshot", "tick": self.tick, "sim_tick": self.tick, "state": self.state,
                "time_left_s": rounded(self.time_left()), "score": self.score,
                "player": {**self.player, "pos": [rounded(v) for v in self.player["pos"]]},
                "lanterns": [{**l, "pos": [rounded(v) for v in l["pos"]]} for l in self.lanterns],
                "shades": [{"id": sh["id"], "pos": [rounded(v) for v in sh["pos"]], "state": "stunned" if self.tick < sh["stun_until"] else "chasing"} for sh in self.shades],
                "motes_active": len(self.motes), "motes": [{"id": m["id"], "pos": [rounded(v) for v in m["pos"]]} for m in self.motes]}
