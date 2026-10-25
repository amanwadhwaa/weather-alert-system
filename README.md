# Weather Alert System with Automated CI/CD

Flask service that polls OpenWeatherMap on a schedule, stores readings in PostgreSQL,
emails you via Postmark when the temperature drops below a threshold, and shows a
dashboard. A GitHub Actions pipeline tests, containerizes, and deploys it on every push.

## Pipeline

```
push to main ─► test (pytest) ─► build Docker image ─► push to GHCR ─► Render deploy hook
                    │ fail            │ fail                │ fail
                    └─────────────────┴─────────────────────┴─► pipeline halts, old version stays live
```

Pull requests run the test job only.

## Run locally

```bash
cp .env.example .env        # fill in API keys
docker compose up --build   # http://localhost:8000
```

Without Docker:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
pytest
SCHEDULER_ENABLED=true flask --app wsgi run
```

## Endpoints

| Path | Description |
|---|---|
| `/` | Dashboard (auto-refreshes) |
| `/api/readings` | Last 50 readings as JSON |
| `/health` | Liveness + DB check (used by Docker and Render) |

## One-time deployment setup

1. **Push to GitHub** (default branch `main`). Actions runs automatically.
2. **Render**: New → Web Service → *Existing image* → `ghcr.io/<your-user>/<repo>:latest`.
   - Add a Render PostgreSQL database and set `DATABASE_URL` from it.
   - Set env vars from `.env.example` (`WEATHER_API_KEY`, `POSTMARK_SERVER_TOKEN`, `ALERT_FROM_EMAIL`, `ALERT_TO_EMAIL`, `CITY`, `TEMP_THRESHOLD_C`).
   - Health check path: `/health`.
   - GHCR packages are private by default: either make the package public (GitHub → Packages → settings) or add GHCR credentials (a PAT with `read:packages`) in Render.
3. Copy the service's **Deploy Hook URL** (Render → Settings) into a GitHub repo secret named `RENDER_DEPLOY_HOOK_URL`.
4. (Optional) Create a GitHub environment named `production` for approval gates.

## Demonstrating the quality gate (Phase 5)

- **Passing push**: commit any change → all three jobs go green and Render redeploys.
- **Failing push**: change `should_alert` in `app/alerts.py` to `<=`, push →
  `test_should_not_alert_at_or_above_threshold` fails, build/deploy jobs are skipped,
  and the previous version keeps serving traffic.

## Project layout

```
app/            Flask app (config, models, weather, alerts, service, routes)
tests/          Pytest suite (all external calls mocked)
Dockerfile      Production image (gunicorn, non-root, healthcheck)
.github/workflows/ci-cd.yml
```

## Future enhancements
Staging/production environments, blue-green deploys, Prometheus + Grafana, automated rollback, security scans (e.g. Trivy, Bandit) before deploy.
