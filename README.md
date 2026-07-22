# Habit Tracker API


An async backend API for tracking habits and daily progress — built with **FastAPI**, **async SQLAlchemy**, **JWT authentication**, and **Redis-backed session revocation**. Designed and built to reflect real production patterns: ownership-scoped access control, email verification, structured logging, and automated tests.

**Live demo:** [add your deployed URL here]
**Repo:** `https://github.com/SixtuNnanna/HabitTracker`

---

## What it does

Think of it as the backend engine behind a habit-tracking app like Habitica or Loop — the part that stores data, enforces rules, and exposes an API for a frontend (or Swagger UI) to consume.

- Users sign up, verify their email, and log in to receive a JWT
- Each user creates and manages their own **habits** (daily / weekly / interval-based schedules)
- Users log completions ("logs") for each habit, one entry per day
- The API computes due-days, missed-days, streaks, and completion-rate trends — all derived live from the schedule + log history, never stored redundantly
- All data is strictly scoped per user — no user can ever read, edit, or delete another user's data

---

## Tech stack

| Layer | Choice |
|---|---|
| Framework | FastAPI (async) |
| ORM | SQLAlchemy 2.0 (async, `Mapped[]` style) |
| Database | SQLite (async, via `aiosqlite`) |
| Migrations | Alembic |
| Auth | JWT (HS256) via `python-jose`, password hashing via `passlib` |
| Session revocation | Redis (token blacklist by `jti`) |
| Validation | Pydantic v2 |
| Testing | pytest, pytest-asyncio, httpx (in-process ASGI client), fakeredis |
| CI | GitHub Actions (lint + test on every push/PR) |

---

## Architecture

```
app/
├── api/
│   ├── routers/        # Route handlers (thin — delegate to services)
│   ├── schemas/         # Pydantic request/response models
│   └── dependencies.py  # Shared FastAPI dependencies (auth, DB session)
├── core/
│   ├── security.py      # JWT creation/verification, password hashing
│   ├── email_token.py         # Generation/Verification Email Url token
│
├── database/
│   ├── models.py         # SQLAlchemy models (User, Habit, HabitLog)
│   ├── base.py            # Declarative base
│   └── session.py         # Async engine + session factory
├── services/              # Business logic — one service per resource
│   ├── base.py             # Generic CRUD service (Generic[ModelType])
│   ├── user.py
│   ├── habits.py
│   └── log.py
├── config.py               # Environment-driven settings (singleton)
└── main.py                  # App entrypoint, startup lifecycle
```

**Design principles followed throughout:**
- **Thin routers, fat services** — routes handle HTTP concerns only (status codes, request/response shape); all business logic lives in services.
- **Ownership scoping at the query level** — every fetch/update/delete filters by the requesting user's ID directly in the SQL `WHERE` clause, not via a fetch-then-check pattern. A user requesting another user's resource gets an identical `404` to a resource that doesn't exist — no information leakage about what IDs exist.
- **Services raise `ValueError`, never `HTTPException`** — keeps business logic decoupled from the HTTP layer; routes translate exceptions into the appropriate status codes.
- **Derived data over stored data** — completion rates, due-days, and streaks are computed live from raw logs + habit schedules rather than cached/duplicated, keeping the data model minimal and always consistent.

---

## Key features

### Authentication & security
- Signup with password strength validation (Pydantic `field_validator`)
- Email verification via signed, time-limited tokens (`itsdangerous`)
- JWT-based login (HS256), with `jti` claims for per-token revocation
- Logout invalidates the specific token via a Redis blacklist (checked on every authenticated request), with TTL matching the token's natural expiry
- Passwords hashed with `passlib` (argon2)
- Login failure messages are intentionally generic (same response for "wrong password" and "email not found") to prevent account enumeration

### Habits & logging
- CRUD for habits with three scheduling types: daily, weekly (specific weekdays), and interval-based (every N days)
- CRUD for habit logs, with a database-level unique constraint preventing duplicate logs for the same habit on the same day
- Partial updates only modify explicitly sent fields — untouched fields are never overwritten with defaults

### Analytics
- Due-day and completion-rate calculation over arbitrary date ranges
- Week-over-week and month-over-month completion trend comparison

---

## Continuous Integration

Every push and pull request against `main` runs automatically via **GitHub Actions** (`.github/workflows/python-app.yml`):
- **Lint** — `flake8`, first a strict pass that fails the build on syntax errors or undefined names, then a full style report
- **Test** — the full `pytest` suite, run against an isolated in-memory database and `fakeredis`, with required secrets injected via GitHub Actions repository secrets (never committed to the repo)

This means every change is verified automatically before it can be merged — no manual "did I break anything" step required.

---

## Getting started

**Prerequisites:** Python 3.12, Redis running locally (`brew install redis && brew services start redis`, or your platform's equivalent).

```bash
git clone https://github.com/[your-username]/HabitTracker.git
cd HabitTracker
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in real values
alembic upgrade head
uvicorn app.main:app --reload
```

API will be available at `http://localhost:8000`, interactive docs at `http://localhost:8000/docs`.

---

## Running tests

```bash
pip install -r requirements-dev.txt
pytest -v
```

The test suite runs against an isolated in-memory SQLite database (created fresh per test) with `fakeredis` standing in for the token blacklist — no external services required. Coverage includes:
- Full auth flow (signup, duplicate-email rejection, login, email verification, logout/token revocation)
- Ownership isolation (a user cannot read, update, or delete another user's habits or logs) — the highest-priority test category in this project, since it locks in the core security guarantee
- Partial-update correctness
- Duplicate-log prevention

---

## API overview

| Method | Path | Description |
|---|---|---|
| POST | `/auth/signup` | Create an account |
| GET | `/auth/verify-email` | Verify email via token link |
| POST | `/auth/token` | Log in, receive JWT |
| POST | `/auth/logout` | Revoke the current token |
| GET | `/me` | Get the current authenticated user |
| POST | `/habit/` | Create a habit |
| GET | `/habit/{habit_id}` | Get a habit by ID |
| PUT | `/habit/{habit_id}/update` | Update a habit (partial) |
| DELETE | `/habit/{habit_id}` | Delete a habit |
| POST | `/habit/{habit_id}/logs` | Log a habit completion |
| GET | `/habit/{habit_id}/logs` | List logs for a habit |
| GET | `/habit/{habit_id}/stats/week` | Weekly completion trend |
| GET | `/habit/{habit_id}/stats/month` | Monthly completion trend |

Full interactive documentation (with request/response schemas) is available at `/docs` once the server is running.

---

## What I'd build next

- Docker + docker-compose for one-command setup (app, Redis, and a Postgres-backed deployment option)
- Interval-based habits with rolling cooldowns (e.g. "every 2 hours") rather than calendar-day granularity
- Streak calculation as a dedicated endpoint
- Rate limiting on auth endpoints
- "Logout everywhere" (revoke all active sessions for a user, not just one token)

---

## Author

[https://github.com/SixtusNnanna] - Sixtus
