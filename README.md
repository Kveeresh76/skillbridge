# SkillBridge

**Knowledge is the new currency.**

SkillBridge is a peer-to-peer skill exchange platform. Instead of paying money to learn,
users teach a skill to earn **Skill Credits**, then spend those credits to learn a skill
from someone else. The platform matches people whose "offered" and "wanted" skills
complement each other.

> **Status:** Phase 2 (database models, migrations, seed data) complete. See [Roadmap](#roadmap) below for what's next.

## Tech stack

| Layer      | Choices |
|------------|---------|
| Frontend   | React 18, Vite, React Router, Tailwind CSS, Axios, Lucide icons |
| Backend    | FastAPI, Pydantic v2, SQLAlchemy 2.0, JWT auth, WebSockets |
| Database   | PostgreSQL, Alembic migrations |
| DevOps     | Docker, Docker Compose, GitHub Actions CI |
| Testing    | Pytest + FastAPI TestClient (backend), Vitest + React Testing Library (frontend) |

## Folder structure

```
skillbridge/
├── backend/
│   ├── app/
│   │   ├── core/        # settings, security (JWT, password hashing)
│   │   ├── database/    # SQLAlchemy engine/session
│   │   ├── models/      # ORM models (added per phase)
│   │   ├── schemas/     # Pydantic request/response models
│   │   ├── api/         # route modules, grouped by domain
│   │   ├── services/    # business logic (matching, credits, notifications)
│   │   └── main.py      # FastAPI app instance
│   ├── alembic/         # DB migrations
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── context/      # AuthContext
│   │   ├── services/     # api.js (Axios client)
│   │   └── App.jsx
│   └── Dockerfile
├── docker-compose.yml
└── .github/workflows/ci.yml
```

## Running locally with Docker (recommended)

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
docker compose up --build
```

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API docs (Swagger): http://localhost:8000/docs
- Postgres: localhost:5432 (user/db: `skillbridge`)

## Running locally without Docker

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then point DATABASE_URL at your local Postgres
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## Database migrations & seed data

```bash
cd backend
alembic upgrade head       # create all tables
python -m app.seed         # populate demo data (15 users, 24 skills, requests,
                            # conversations, sessions, reviews, transactions, notifications)
```

Every seeded user shares the same demo password, printed by the seed script when it runs.
Seed data is for local development only — never run `app.seed` against a production database
(it clears existing rows first, in FK-safe order, so it's safe to re-run in dev).

## Testing

```bash
# backend
cd backend && pytest -q

# frontend
cd frontend && npm test
```

## Production deployment

The development Compose file runs Vite and mounts source code. For deployment,
copy `.env.production.example` to `.env` and
`backend/.env.production.example` to `backend/.env`, then replace every
placeholder with real values. In particular, use a unique database password,
a long random `JWT_SECRET_KEY`, and the public frontend origin for
`CORS_ORIGINS`.

Build and start the production stack:

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

The migration service applies Alembic migrations before the backend starts.
The frontend is served by Nginx on `APP_PORT` (default `80`) and proxies `/api`
to the backend. Do not run `python -m app.seed` in production; it deletes and
recreates development data.

For HTTPS, place a managed TLS proxy or load balancer in front of the app and
set `CORS_ORIGINS` to the HTTPS origin. Back up the `postgres_data` volume
before upgrades.

## Environment variables

See `backend/.env.example` and `frontend/.env.example`. Never commit a real `.env` file —
`JWT_SECRET_KEY` in particular must be a long random value in any non-local environment.

## Roadmap

- [x] Phase 1 — Project setup
- [x] Phase 2 — Database models, Alembic migrations, seed data (this state)
- [ ] Phase 3 — Authentication (register/login/JWT/profile)
- [ ] Phase 4 — Skills system (offered/wanted, proficiency)
- [ ] Phase 5 — Matching + Discover page
- [ ] Phase 6 — Exchange requests
- [ ] Phase 7 — Real-time chat + notifications
- [ ] Phase 8 — Session scheduling
- [ ] Phase 9 — Skill Credits + transactions
- [ ] Phase 10 — Ratings & reviews
- [ ] Phase 11 — Dashboard
- [ ] Phase 12 — AI features (smart matching, roadmaps, session summaries)
- [ ] Phase 13 — Testing hardening
- [ ] Phase 14 — Production deployment

## License

MIT
