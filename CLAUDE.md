# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
uv sync

# Start PostgreSQL + Redis
docker-compose up -d

# Initialize DB and populate nominees
uv run db-populate

# Run the bot
uv run bot-run

# Format code
ruff format src/

# Lint
ruff check src/

# Type check
ty check src/
```

PostgreSQL runs on `127.0.0.1:5434`, Redis on `127.0.0.1:6379` via docker-compose.

## Architecture

**Entry point**: `src/main.py` — initializes bot, DB pool, asyncio queue (max 35 items), Google Sheets OAuth, background worker, and starts polling.

**Request pipeline** (middleware order matters):
1. `UpdatesDumperMiddleware` (outer) — logs raw updates as JSON
2. `DBSessionMiddleware` — injects async SQLAlchemy session as `db_session`
3. `AuthMiddleware` — gets/creates `User` record

**Vote flow** (multi-select, 3 nominees per nomination):
- User selects a nomination → `VotingStates.selecting_nominees` FSM state activated
- Toggle buttons: 🔵 when < 3 selected, 🟢 when all 3 selected (FIFO eviction on 4th tap)
- "Проголосовать ✅" button appears only when exactly 3 selected
- Submit creates `Vote(vote_for_1, vote_for_2, vote_for_3)` in DB

**Admin commands** (only for user with `ADMIN` telegram_id):
- `/export` — generates and sends `.xlsx` with all votes (phone | nomination | 3 nominees | datetime)
- `/broadcast <text>` — sends text message to all users with rate limiting

**Database models** (`src/database/models.py`):
- `User`: `telegram_id`, `phone_number`, `voted_1..voted_13` boolean flags
- `Nominee`: `name`, `last_name`, `link`, `nomination` (IntEnum 1-13)
- `Vote`: `(user_id, nomination)` unique — one row per user per nomination, with `vote_for_1/2/3` FKs

**FSM storage**: Redis (DSN from env). State stores `{msg_id, nomination, selected_ids: list[int]}`.

**Nominations** are placeholders in `src/bot/internal/enums.py` (13 entries). Replace with real 2026 data. Nominee data in `src/database/tables_helper.py`.

## Environment

Copy `example.env` → `.env` and fill in:
- `BOT_TOKEN` — from Telegram @BotFather
- `ADMIN` — Telegram user ID for error notifications and admin commands
- `STAGE` — `PROD` or `DEV`
- `DATABASE_DSN` — `postgresql+asyncpg://user:pass@host:port/db`
- `REDIS_DSN` — `redis://localhost:6379/0`

## Code style

- Black: line-length=120, skip-string-normalization, target py311
- Ruff: line-length=120, select ALL (see pyproject.toml for ignores)
- All service/handler methods must be async
- Pydantic for task schemas (`src/bot/internal/schemas.py`): `VoteTask`, `CounterTask`
