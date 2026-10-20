# Bus

Shared event hub. Envelope fields are frozen in [`docs/04-interfaces.md`](../docs/04-interfaces.md).

## Install and run

```bash
cd bus
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python run_hub.py --port 9000
```

- `POST http://127.0.0.1:9000/publish` publishes an envelope
- `ws://127.0.0.1:9000/ws` subscribes
- The hub appends `bus/bus_events.jsonl` (gitignored)

`orchestrator/run_spine.py` starts this hub itself, along with the mocks and the cloud bridge. Use that when you want the scripted Night Watch path, and run this hub alone when a live robot bridge should subscribe. One process can bind port 9000.
