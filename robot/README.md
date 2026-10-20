# Robot bridges

Perception and Unitree / DimOS stay in this folder and in `hackmitdog/`. The portal does not import those SDKs. Video is out of band: do not add camera frames to `/api/ingest`.

## Dog camera

Night Watch shows a live view when a caregiver opens **View dog camera**.

| | |
|---|---|
| Cloud env | `DOG_CAMERA_ENABLED=1` and `DOG_CAMERA_URL` for an iframe page |
| Alternate | `DOG_CAMERA_STREAM_URL` for `GET /api/camera/stream` |
| Bus | Map and track events still use `/api/ingest` |

A DimOS cockpit is one viewer that satisfies `DOG_CAMERA_URL`. Restart the API after changing `cloud/.env`. Diagnostics: [`CAMERA_DIAGNOSTICS.md`](CAMERA_DIAGNOSTICS.md).

## Command bridge

Run one DimOS blueprint that exposes the Aegis and breadcrumb tools, then:

```bash
python robot/dimos_command_bridge.py --bus-url ws://127.0.0.1:9000/ws
```

Handled actions:

| Bus action | MCP calls |
|---|---|
| `follow_person` | `start_breadcrumb_recording`, then `follow_person` |
| `guide_home` | `stop_person_follow`, then `take_me_home` |
| `stop` | `stop_person_follow` |
| `posture` with `command_name` | `execute_sport_command` |

Anything else is reported as an unsupported action, including Night Watch `lead_to`.

The phone walk path is [`VOICE_WALK_RUNBOOK.md`](VOICE_WALK_RUNBOOK.md).

## Map bridge

`map_room` runs bounded frontier exploration and writes `<map_id>.ply` plus `<map_id>.json`. Onboarding **Start mapping** publishes `map_scan_request` with a live mode. This process turns that into the MCP call and posts `map_ready`:

```bash
python robot/dimos_map_bridge.py \
  --bus-url ws://127.0.0.1:9000/ws \
  --cloud-base http://127.0.0.1:8000 \
  --artifact-dir artifacts/maps \
  --artifact-base /api/maps
```

The PLY has to land in the cloud process’s artifact directory (default `artifacts/maps`, or `LANTERN_MAP_ARTIFACT_DIR`). **Stop & use current map** sends command action `stop`; the bridge calls `end_exploration` and the skill exports the partial cloud. The explorer has no resume of the same scan session.
