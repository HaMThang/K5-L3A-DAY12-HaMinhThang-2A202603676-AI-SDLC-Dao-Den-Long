# Phase 4 verification evidence

Date: 2026-11-20  
Environment: Windows 11, Python 3.12.10

## Automated checks

| Requirement | Command / check | Observed result |
|---|---|---|
| Python source compiles | `python -m compileall -q src` | Exit code 0; no output |
| Existing regression tests | `python -m unittest discover -s tests -q` | 13 tests passed in 0.193 s |
| Headless contract smoke run | `python -m src.headless --seed 1 --night 2 --ticks 60 --out %TEMP%\dao-den-long-phase4-contract.jsonl` | End record: `{"type":"end","ticks":60,"state":"playing","score":0}` |
| UI source encoding | UTF-8 metadata, Vietnamese language, no replacement characters, C1 controls, or known mojibake signatures; expected UI labels checked | Passed for title, settings, and gameplay messages |
| JavaScript syntax | Extracted inline script and parsed with Node `vm.Script` | Passed |
| Firefly texture route | Start `python -m src.server --port 0`; GET `/assets/firefly-wisp.png` | HTTP 200, `image/png`, 577,659 bytes; PNG signature valid; alpha channel range 0–254 |
| Obstacle collision rules | `Game.obstacle_at` checked at obstacle center at ground and airborne heights | Wood: blocked at ground, passable at y=0.5; rock: blocked at ground and y=2 |
| Patch whitespace | `git diff --check` | Passed; Git only reported expected LF-to-CRLF normalization notices |

## Limitations

- The browser automation host was unavailable, so the WebGL scene and generated sprite were not visually verified in-game.
- The Phase 4 Claude artifact / Ticket-04 could not be accessed. No Ticket-04-specific numeric target is known or claimed here.
- No clean-room browser run, Git tag, GitHub Release, or demo video was produced in this run.

## Follow-up: visibility and start screen (2026-11-20)

- Replaced the centered text-only opening panel with a responsive, left-aligned title screen, start/settings/leaderboard actions, locked night cards, and control hints. The existing simulation state remains rendered behind a translucent scene overlay.
- Matched WebGL varying precision in both shader stages and added a `LINK_STATUS` check that reports shader link errors in the visible HUD instead of silently leaving an empty scene.
- Python regression suite rerun: 13 tests passed. `python -m compileall -q src`: exit code 0.
- Inline JavaScript parsed with Node `vm.Script`: passed.
- Local HTTP smoke check: `/` served the UTF-8 game page; `/state` returned night 1 in `playing` state with 5 lanterns and 20 motes; POST `/start` for night 1 returned `playing` with 5 lanterns.
- The browser automation host was still unavailable in this run, so the final WebGL image and click-through were not visually inspected. The shader now exposes a clear visible error if the GPU rejects the program, but that is not a substitute for a browser visual check.

## Follow-up: fuel lighting and environment density (2026-11-20)

- Replaced the global bright ambient term with per-lantern point lights, scaled by remaining fuel. Unlit map ambient is low; a small handheld light keeps the player visible. Terrain is tessellated into 32 rings x 96 sectors so lighting near lanterns is interpolated locally instead of across a single large triangle fan.
- Kept fuel simulation and contract tuning unchanged. Manual headless check: a 100% lit lantern reads 99% after 60 simulation ticks and remains lit.
- Increased physical obstacle count from 5/5/6 to 13 on each map. Added deterministic per-obstacle log length variation, raised splinter branches and cut ends for fallen logs, irregular faceted rock geometry, and more palm/forest dressing.
- Regression tests: 13 passed. Python compile check and `git diff --check`: exit code 0. Inline JavaScript parsed successfully with Node `vm.Script`.
- Browser visual verification remains unavailable in this environment; the lighting code is source-checked but its exact appearance and frame rate still need a browser run.

## Follow-up: user-supplied Archangel and fuller maps (2026-11-20)

- Read `light-archangel-artamiel.zip`; it contains `archangel-light.obj`, `archangel-light.mtl`, and a 512x256 RGBA atlas. Copied these into `src/assets/`; the server now serves the OBJ and atlas.
- Added a browser-side OBJ/UV parser and textured WebGL mesh for M?y. Added a straw conical hat, emissive rendering, and a character-centered point light; removed the handheld lantern from the player model. Island lanterns still use their own fuel-scaled local lights.
- Added deterministic batches of grass tufts and wildflowers per map, and changed Map 3 tree silhouettes to four layered foliage tiers.
- Parsed the full inline JavaScript and independently parsed the OBJ: 1,844 triangles, 5,532 expanded vertices/UVs. Existing suite: 13 tests passed; Python compile check passed.
- The supplied archive had no license file; this provenance is recorded in `CREDITS.md`. Browser rendering of the imported model still needs direct visual confirmation because browser automation is unavailable here.

## Follow-up: upright player, houses, and Map 3 mountains (2026-11-20)

- Corrected OBJ axis conversion to use the asset's Y-up coordinate system; moved the conical hat to sit on the imported head.
- Added two collidable wooden houses to each map and five collidable rocky mountain peaks on Map 3. Existing map boundaries and elevated-floor rules were left unchanged.
- Headless collision smoke check: all 6 house centers and 5 mountain centers block movement; all three default spawn positions remain unblocked.
- Regression suite: 13 passed. Python compile check and `git diff --check` passed. Browser image was not captured in this run.
