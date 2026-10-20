# Dog camera checks

Example of reading `GET /api/camera/status` and checking a local viewer. The addresses below are placeholders. `cloud/server/camera.py` returns `enabled`, `master_enabled`, `url`, `stream_url`, `proxy_stream`, and `hint`.

With `DOG_CAMERA_ENABLED=1` and a viewer URL set, status looks like this:

```json
{
  "enabled": true,
  "master_enabled": true,
  "url": "http://127.0.0.1:9877/",
  "stream_url": null,
  "proxy_stream": null,
  "hint": "Caregiver must open View dog camera — feed is not always-on."
}
```

That shows the API read `DOG_CAMERA_ENABLED` and `DOG_CAMERA_URL`, and that the portal may offer the camera control. It does not show that port `9877` serves a page a browser can embed.

A process listening on the port is a separate check:

```bash
lsof -nP -iTCP:9877 -sTCP:LISTEN
```

That shows something owns the port. It does not show valid HTTP, a camera viewer, or an iframe-compatible page.

## Run these checks in order

Run them on the computer where the viewer process is running. Open the viewer URL in a browser.

```bash
curl -v --max-time 5 http://127.0.0.1:9877/
```

```bash
lsof -nP -iTCP:9877 -sTCP:LISTEN
```

Interpretation:

| Result | Meaning | Next step |
|---|---|---|
| Connection refused or timeout | Listener is not serving HTTP correctly | Check the DimOS/cockpit process logs and startup command |
| HTTP 404/plain text | Port is not the viewer root | Find the actual cockpit/WebRTC viewer path |
| A working viewer page | DimOS viewer is alive | Check iframe policy and browser console errors |
| Redirect/login page | Viewer needs a session or authentication | Open and authenticate the viewer directly first |

## Check the Lantern API configuration

```bash
curl http://127.0.0.1:8000/api/camera/status
```

Example when only the viewer URL is set:

```json
{
  "enabled": true,
  "master_enabled": true,
  "url": "http://127.0.0.1:9877/",
  "stream_url": null,
  "proxy_stream": null,
  "hint": "Caregiver must open View dog camera — feed is not always-on."
}
```

If the values are wrong, set `cloud/.env`:

```dotenv
DOG_CAMERA_ENABLED=1
DOG_CAMERA_URL=http://127.0.0.1:9877/
```

Restart the API after changing `.env`, from the repository root:

```bash
source .venv/bin/activate
python -m uvicorn main:app --app-dir cloud/server --reload --host 0.0.0.0 --port 8000
```

## Browser and network checks

If the viewer URL works in a browser tab and the embedded panel is blank, open the browser console and look for:

```text
Refused to display ... in a frame
```

That means the DimOS page sends `X-Frame-Options` or CSP that blocks iframe embedding. The portal embeds `DOG_CAMERA_URL` in an iframe. It does not copy camera frames itself.

If the portal is opened from another computer or phone, `127.0.0.1` is that device, not the robot computer. Use the robot computer's LAN address:

```dotenv
DOG_CAMERA_URL=http://192.168.12.X:9877/
```

The robot computer must allow inbound TCP traffic on that port.

If the portal is HTTPS, an HTTP camera URL may be blocked as mixed content. In that case the viewer must also be exposed over HTTPS.

## Raw stream fallback

If the DimOS viewer cannot be embedded, configure a raw MJPEG or similar stream endpoint instead:

```dotenv
DOG_CAMERA_ENABLED=1
DOG_CAMERA_STREAM_URL=http://127.0.0.1:9877/<actual-stream-path>
```

Restart the API, then check:

```bash
curl -I http://127.0.0.1:8000/api/camera/stream
```

The portal uses the same-origin `/api/camera/stream` proxy when `DOG_CAMERA_STREAM_URL` is set. Status then sets `proxy_stream` to `/api/camera/stream`.

## What the example leaves open

A status payload that points at `127.0.0.1:9877` does not say whether that port is an HTTP camera viewer, a WebRTC signaling endpoint that needs a different path, or a page that disallows iframe embedding. The decisive result is:

```bash
curl -v --max-time 5 http://127.0.0.1:9877/
```

The phone, orchestrator, and DimOS command bridge are not required to display video. Video needs a reachable, browser-compatible viewer or raw stream URL.
