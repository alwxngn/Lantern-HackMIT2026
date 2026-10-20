# Portal and phone

The React portal is the caregiver UI. The voice service is mounted in the cloud API at `/voice`. Install, environment variables, and the tunnel are in the [root README](../README.md).

## Processes

```bash
python -m uvicorn main:app --app-dir cloud/server --host 127.0.0.1 --port 8000
npm --prefix cloud/web run dev
```

Open http://127.0.0.1:5173/. `/voice/` redirects to the portal. Provider status is `/voice/api/health`.

## Pairing

1. Open the portal on the HTTPS tunnel origin when the phone is a separate device.
2. Connect a phone from the check-in control and scan the QR, or open the pairing link.
3. Tap **Start Lantern** and leave the page in the foreground.
4. Send a message. The phone plays it, then records a reply for up to five seconds. A typed reply is also available.
5. The transcript shows up in the check-in thread and the Night Watch timeline.

Set `VITE_PUBLIC_ORIGIN` in `cloud/web/.env.local` to the tunnel origin and restart Vite. Point `ACK_BASE_URL` at the same origin when acknowledgement links should open on a phone.

Robot requests use the phone’s separate control (ten-second recording). The API needs `LANTERN_ORCH_PUBLISH_URL` set to the bus, and the bus, orchestrator, and command bridge have to be running. See [the walk runbook](../robot/VOICE_WALK_RUNBOOK.md).

Check-ins are accepted in `IDLE` and `ATTEND`. Other safety states reject them instead of queueing.

## Checks

```bash
python -m unittest discover -s voice/tests -v
npm --prefix cloud/web run build
```
