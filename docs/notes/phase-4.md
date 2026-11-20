# Phase 4 — Release readiness

## Source and scope

The Claude lab board link was supplied with the request, but its Phase 4 artifact could not be fetched: the web reader rejected the Claude artifact URL and the connected browser host was unavailable. No Ticket-04 contents are checked into this repository. This note therefore records only the generic Phase 4 requirements in `CHECKPOINTS.md`; it does not claim the ticket-specific requirements are complete.

## Work completed from the repository checkpoint

- Added a clean-clone game quick start to the root README; running the game requires Python 3.10+ and a WebGL browser, with no extra Python packages.
- Repaired Vietnamese UI strings that had been stored as mojibake in `src/index.html`; the document declares UTF-8.
- Added the complete MIT license and documented procedural scenery plus the user-supplied Archangel model in CREDITS.md.
- Ran the Python build check, all existing unit tests, and the headless contract command; results are recorded in `docs/proof/phase-4.md`.

## Still needs Ticket-04 and/or external release access

- Apply and verify any numeric acceptance thresholds in Ticket-04. They are unknown until the ticket is available.
- Verify a clean clone with the intended user-facing browser flow.
- Create/push the `phase-4` tag and publish GitHub Release `v1.0.0` only after reviewing the exact release checklist and attached artifacts.
- Record/attach the requested sub-five-minute demo video.

