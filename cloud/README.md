# Cloud and caregiver portal

FastAPI app in `cloud/server` and the React portal in `cloud/web`. Full install, environment variables, and the phone tunnel are in the [root README](../README.md).

The API mounts phone audio at `/voice`. Run that one process on port 8000. A second voice server on the same port will not share its sessions.

## Install

Python 3.12+ and Node 20.19+ or 22.12+ (Vite 8).

The API imports the mounted voice package, so use one environment at the repository root. Full environment variables are in the [root README](../README.md).

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r cloud/requirements.txt -r voice/requirements.txt -r orchestrator/requirements.txt -r bus/requirements.txt
npm --prefix cloud/web ci
cp cloud/.env.example cloud/.env
```

## Run

```bash
# Terminal 1, repository root, with the venv active
source .venv/bin/activate
python -m uvicorn main:app --app-dir cloud/server --host 127.0.0.1 --port 8000

# Terminal 2
npm --prefix cloud/web run dev
```

| URL | Screen |
|---|---|
| http://127.0.0.1:5173/ | Welcome |
| http://127.0.0.1:5173/onboarding | Map, zones, routine |
| http://127.0.0.1:5173/watch | Night Watch |

**Start mapping** posts `mode: live`. **Use demo map** posts `mode: demo` and returns a schematic floor plan. `MAP_SCAN_MODE` applies only when the request omits a mode.

Fixture replay, from the repo root with the API already up:

```bash
python cloud/server/replay.py --fixture cloud/fixtures/exit_seeking.jsonl --rate 4
```

`POST /api/reset` clears the JSONL projection, timeline, alerts, ladder timers, and the check-in queue.

Phone pairing, Twilio, the dog camera, and live map artifacts are documented in the [root README](../README.md), [`docs/16-e3-portal.md`](../docs/16-e3-portal.md), and [`robot/README.md`](../robot/README.md).
