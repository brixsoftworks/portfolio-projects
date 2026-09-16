# Deploy to your college server (free self-hosting)

Quacko runs as a single container: an Express server that serves both the **REST API** and
the **website** (the exported Expo web app). Persistence is a SQLite file on a Docker
volume. Everything below costs nothing to host.

```
                    ┌────────────────────────────────────────────┐
 Browser / Native   │  quacko:latest (single container)          │
 ─────────────────► │  ┌──────────────────────────────────────┐  │
                    │  │ Express                              │  │
                    │  │  /api/v1/auth/{register,login,me}   │  │
                    │  │  /api/v1/rpc       (JSON-RPC, JWT)   │  │
                    │  │  /api/v1/uploads   (proof media)     │  │
                    │  │  /                 (website SPA)     │  │
                    │  └───────────────┬──────────────────────┘  │
                    │                  ▼                          │
                    │        better-sqlite3 → /data/quacko.db     │
                    │        (volume: quacko_quacko-data)         │
                    └────────────────────────────────────────────┘
              optional: caddy:2 (auto HTTPS via Let's Encrypt, free)
```

## Requirements

- A machine (college box, VPS, old laptop) with **Docker** + **Docker Compose v2**.
- A domain name **only if** you want HTTPS (Caddy + Let's Encrypt, free).
  Without one, run plain HTTP on a port; the site works identically.

## 1. Get the code onto the server

```bash
git clone <your-repo-url> quacko && cd quacko
```

or copy the folder with `rsync -av --exclude node_modules --exclude .git ./ user@server:~/quacko`.

## 2. Configure

```bash
cp .env.example .env
# REQUIRED: a long random JWT secret (16+ chars)
openssl rand -base64 32   # paste into JWT_SECRET=
nano .env                 # set PUBLIC_URL, TIMEZONE, (DOMAIN for TLS), optional AI_API_KEY/AI_MODEL
```

| Variable | Meaning |
| --- | --- |
| `JWT_SECRET` | Signs auth tokens. Keep it secret and **stable across redeploys** or everyone is logged out. |
| `PUBLIC_URL` | Public origin of the site (used for absolute upload links). e.g. `https://quacko.college.edu` |
| `TIMEZONE` | IANA zone used for streaks/"today", e.g. `Asia/Kolkata`. |
| `PORT` | Host port when running without TLS (default 8787). |
| `DOMAIN` | Enables the optional Caddy HTTPS profile. Must resolve to this server. |
| `AI_API_KEY` / `AI_BASE_URL` / `AI_MODEL` | Optional LLM coach. **Leave empty for free** — the deterministic offline coach is used. |

## 3. Deploy

Without TLS (plain HTTP on `http://<server>:8787`):

```bash
./scripts/deploy-college.sh
```

With HTTPS (set `DOMAIN` first):

```bash
./scripts/deploy-college.sh --with-tls
```

That builds the image (exported website + bundled server + pruned prod deps), starts
`quacko`, and — with `--with-tls` — a Caddy reverse proxy that fetches free Let's Encrypt
certificates automatically.

Verify:

```bash
curl http://<server>:8787/api/v1/health   # → {"ok":true,...}
```

The admin/ops cheatsheet:

```bash
docker compose logs -f quacko      # logs
docker compose ps                   # status
docker compose up -d --build        # rebuild + restart after git pull
docker exec quacko-quacko-1 sh -c 'ls /data'   # sqlite + uploads live here
docker volume ls | grep quacko     # persistent data volume
```

## 4. Point the app & website at it

- **Website:** immediately live at the origin above (login/register built in).
- **Native app (Expo):** set
  `EXPO_PUBLIC_DEMO_MODE=0` and `EXPO_PUBLIC_API_URL=https://quacko.college.edu`
  in `apps/mobile/.env` and build/`eas update` as usual. On web the API URL may be left
  empty (same origin).

## Notes & safety

- **Backup:** the whole state is one file — `docker run --rm -v quacko_quacko-data:/d -v $PWD:/b alpine cp /d/quacko.db /b/`. Schedule it with cron if the data matters.
- **Updates:** `git pull && docker compose up -d --build` (data volume survives).
- **Resource use:** one Node process + SQLite. Fits comfortably on 512 MB RAM.
- **No cost:** Docker runtime only; Caddy certs and the optional AI coach are the only
  external services, and both are optional/free-tier friendly.

## Reaching the admin/owner

There are no admin accounts yet — every account is a regular user. (Roadmap.)