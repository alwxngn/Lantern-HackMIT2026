# Voice

Phone microphone, speaker, and session relay. In the combined app the cloud API mounts this package at `/voice`. Use the [root README](../README.md) for that setup. Do not also run `voice.app` on port 8000.

[`PORTAL_SETUP.md`](PORTAL_SETUP.md) is the short portal-plus-phone checklist.

## Standalone server

Useful for the standalone pages in `voice/static/` without the React portal. From the repository root, with `voice/requirements.txt` installed:

```bash
python -m uvicorn voice.app:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000, create a session, and open the phone link. Tap **Start Lantern** before sending a check-in. A physical phone needs an HTTPS tunnel to this process, and the caregiver page has to be opened on that HTTPS origin before the phone link is copied.

Copy [`voice/.env.example`](.env.example) to `.env` at the repository root. `voice/app.py` loads that file with `override=True`. Restart after edits.

| Variable | Effect |
|---|---|
| `DEEPGRAM_API_KEY` | Upload the finished recording for transcription |
| `DEEPGRAM_MODEL` | Default `nova-3` |
| `ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID`, `ELEVENLABS_VOICE_CONSENT=true` | Server speech. All three are required |
| `ELEVENLABS_MODEL_ID` | Default `eleven_flash_v2_5` |

Check-in capture stops after **five seconds**. Robot-request capture stops after **ten seconds**. Uploads larger than 5 MiB are rejected. The provider calls transcribe a completed recording.

Onboarding voice enrollment lives on the cloud route `POST /api/onboarding/voice-clone`, which calls ElevenLabs `/v1/voices/add`. The standalone caregiver page does not collect that sample.

Replies from `voice/dialogue.py` are one fixed sentence. Keyword matching flags a few distress words for the caregiver view.

```bash
python -m voice.check_providers
```

That command places one short synthesis call and one transcription call.

## What the session does

1. Create a session. The server returns separate caregiver and phone tokens.
2. The phone stores its token from the URL fragment, then strips the fragment.
3. A check-in is delivered as a `say` payload. The phone reports speaking, delivered, interrupted, or failed.
4. After a check-in clip finishes, the phone records a reply. Typed replies work as well.
5. Turn ids drop duplicate replies. Check-in ids drop replies for an older check-in.

Sessions stay in memory, expire after 12 hours, and allow one phone. Run a single worker.

## Tests

```bash
python -m unittest discover -s voice/tests -v
node --check voice/static/phone.js
node --check voice/static/caregiver.js
```

Provider calls in the unit tests are mocked. `voice/tests/browser_smoke.py` needs Playwright and a server without provider keys. `voice/tests/live_browser_smoke.py` and `voice/tests/portal_browser_smoke.py` spend provider credits.
