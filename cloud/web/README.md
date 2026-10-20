# Night Watch portal

React and Vite UI under `cloud/web`. The API has to be running. Install and environment variables are in the [root README](../../README.md) and the [cloud README](../README.md).

## Prerequisites

- Node.js 20.19+ or 22.12+
- API on `http://127.0.0.1:8000`

## Install and run

```bash
cd cloud/web
npm ci
npm run dev
```

Open http://127.0.0.1:5173.

| Path | Screen |
|---|---|
| `/` | Welcome |
| `/onboarding` | Map, zones, routine |
| `/watch` | Night Watch |

Vite proxies `/api`, `/ws`, and `/voice` to port 8000.

For a phone tunnel, copy [`.env.example`](.env.example) to `.env.local` and set `VITE_PUBLIC_ORIGIN`. Restart Vite after changing it.

```bash
npm run build
npm run preview
npm run lint
```

Shipped colors and type are in [`design.md`](design.md) and `src/index.css`.
