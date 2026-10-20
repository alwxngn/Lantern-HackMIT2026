# Cloud and caregiver portal

FastAPI app in `cloud/server` and the React portal in `cloud/web`. Full install, environment variables, and the phone tunnel are in the [root README](../README.md).

The API mounts phone audio at `/voice`. Run that one process on port 8000. A second voice server on the same port will not share its sessions.

## Install

Python 3.12+ and Node 20.19+ (or 22.12+).

```bash
cd cloud
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
cd web && npm install
```

Voice, bus, and orchestrator requirements are separate files. The root README installs all of them into one environment, which is the setup the combined app expects.

## Run

```bash
# Terminal 1, from cloud/ with the venv active
cd server && uvicorn main:app --host 127.0.0.1 --port 8000

# Terminal 2
cd cloud/web && npm run dev
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
