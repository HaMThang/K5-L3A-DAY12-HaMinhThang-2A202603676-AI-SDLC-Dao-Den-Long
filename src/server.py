"""Local browser game server; the simulation stays in src.game."""
import json
import argparse
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from .game import Game

ROOT = Path(__file__).resolve().parent
game = Game()
total_score = 0
lock = threading.Lock()
prior = {key: False for key in ("jump", "interact", "pulse", "dash", "pause")}


class Handler(BaseHTTPRequestHandler):
    def respond(self, data, status=200, content_type="application/json"):
        payload = data if isinstance(data, bytes) else json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if self.path == "/":
            self.respond((ROOT / "index.html").read_bytes(), content_type="text/html; charset=utf-8")
        elif self.path in ("/assets/firefly-wisp.png", "/assets/archangel-light.png", "/assets/archangel-light.obj"):
            name = self.path.rsplit("/", 1)[-1]
            asset = ROOT / "assets" / name
            content_type = "text/plain; charset=utf-8" if name.endswith(".obj") else "image/png"
            self.respond(asset.read_bytes(), content_type=content_type)
        elif self.path == "/state":
            with lock: self.respond(game.snapshot())
        else: self.respond({"error": "not found"}, 404)

    def do_POST(self):
        global game, prior, total_score
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))))
            with lock:
                if self.path in ("/restart", "/start", "/next"):
                    if self.path == "/start":
                        night = int(body.get("night", 1))
                        total_score = 0
                    elif self.path == "/next":
                        if game.state != "won" or game.night >= 3:
                            self.respond({"error": "next night unavailable"}, 400)
                            return
                        total_score += game.score
                        night = game.night + 1
                    else: night = game.night
                    game = Game(night=night)
                    prior = {key: False for key in prior}
                elif self.path == "/step":
                    buttons = {key: bool(body.get(key, False)) for key in prior}
                    edges = {key: buttons[key] and not prior[key] for key in prior}
                    controls = {"move": body.get("move", [0, 0]), "cam_yaw_deg": body.get("cam_yaw_deg", 0), **buttons}
                    game.step(controls, edges)
                    prior = buttons
                else:
                    self.respond({"error": "not found"}, 404)
                    return
                self.respond({"snapshot": game.snapshot(), "events": game.events, "total_score": total_score + game.score})
        except (ValueError, TypeError, KeyError) as exc:
            self.respond({"error": str(exc)}, 400)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=0, help="TCP port; 0 selects a free port")
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Dao Den Long: http://127.0.0.1:{server.server_port}", flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()


if __name__ == "__main__": main()
