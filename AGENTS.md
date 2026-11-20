# Agent instructions

## Project

- Game: Đảo Đèn Lồng, developed for the Day 12 AI SDLC lab.
- Read the current phase requirements and Test Contract before changing code.
- The root `README.md` currently contains the lab brief. Add game setup and run instructions there when the implementation is ready.

## Commands

Replace these placeholders when choosing the engine and test runner:

- Build: `python3 -m compileall -q src`
- Run: `python3 -m src.server` then open the printed URL (a free port is selected automatically)
- Tests: `python3 -m unittest discover -s tests -v`
- Headless contract v1.1: `python3 -m src.headless --seed 1 --night 2 --ticks 60 --out result.jsonl`

## Working rules

- Keep gameplay logic independent from rendering so it can run headless.
- Keep `game.contract.json` tuning values in sync with actual gameplay values.
- Phase 2 uses Ticket-02 standard values and supports `--night 1|2|3`; do not restore Phase 1 chosen values.
- Do not change or remove a test just to make a failing implementation pass.
- Run relevant tests and record real evidence before claiming a requirement is complete.
- Keep phase assumptions, AI usage, and evidence in `docs/`.
- Never commit `.env`, API keys, tokens, or other secrets.
