# Orchestrator

Night Watch state machine, walk intents, mocks, and the cloud bridge. Schemas: [`docs/04-interfaces.md`](../docs/04-interfaces.md). Robot install is in the [root README](../README.md).

States: `IDLE`, `ATTEND`, `LEAD`, `ESCALATE`, `EMERGENCY`, plus `WALK`, `FOLLOW`, `CONFIRM_HOME`, and `GUIDE_HOME`.

## Install

```bash
cd orchestrator
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

`run_spine.py` puts `../bus` on `PYTHONPATH`.

## Mock spine

Terminal 1, cloud API on port 8000 (see [`cloud/README.md`](../cloud/README.md)). Terminal 2, optional portal at http://127.0.0.1:5173/watch. Terminal 3:

```bash
cd orchestrator && source .venv/bin/activate
python run_spine.py --scenario exit_seeking
```

The runner starts a hub on port 9000, `mock_patient`, `mock_robot`, the state machine, and a bridge that `POST`s every message to `http://127.0.0.1:8000/api/ingest`. Twilio sends or dry-runs from the cloud process. A portal acknowledgement cancels the ladder.

```bash
python verify_spine.py
```

`verify_spine.py` expects the API on port 8000.

## Standalone mocks

Start `python ../bus/run_hub.py` first.

```bash
python mocks/mock_patient.py --scenario exit_seeking --hub http://127.0.0.1:9000
python mocks/mock_robot.py --fail-rate 0
```

## Live robot, no mocks

```bash
python run_orchestrator.py --bus-url ws://127.0.0.1:9000/ws --cloud http://127.0.0.1:8000
```

This process publishes a startup config. The patient name in that default is Arthur, while the portal default is Susan. Push the household config after startup when both are running.

DimOS blueprints are registered in the repo `pyproject.toml`. Install this repo into the virtualenv that already has DimOS (`pip install -e .` or `uv pip install -e .` from the repository root), then `dimos run` the blueprint you want. `hackmitdog.breadcrumb` is the combined non-LLM entry. `hackmitdog.aegis-breadcrumb-agentic` adds an MCP client. Pass that install’s robot address, AES key, and model flags. Do not start `MockRobot` on the same bus.
