## Purpose
This file provides short, actionable guidance for AI coding agents working in this repository so they can be productive without hand-holding.

## Big picture (what this repo is)
- A small Django web project created with `django-admin startproject`.
- Project package: `chess_analyzer/` (contains `settings.py`, `urls.py`, `wsgi.py`, etc.).
- Single app directory: `chess_analyzer/ChessAnalyzer/` (models, views, admin, tests, migrations).
- Database: SQLite file at `db.sqlite3` in the repository root.

Key files to inspect first: `manage.py`, `chess_analyzer/settings.py`, `chess_analyzer/urls.py`, and `chess_analyzer/ChessAnalyzer/` (models, views, admin).

## Developer workflows and commands (explicit)
- Create & activate a venv (macOS/zsh):
```
python3 -m venv venv
source venv/bin/activate
pip install Django==5.1.7
```
- Run database setup and dev server:
```
python manage.py migrate
python manage.py runserver
```
- When adding or changing models:
```
python manage.py makemigrations ChessAnalyzer
python manage.py migrate
```
- Tests (project currently has no test suite wired; command still valid):
```
python manage.py test
```

## Project-specific conventions & gotchas
- The app folder is named `ChessAnalyzer` (CamelCase). When importing or adding it to `INSTALLED_APPS`, use the app config path found in `chess_analyzer/ChessAnalyzer/apps.py` (inspect that file to confirm `name = ...`).
- `settings.py` currently has only Django contrib apps in `INSTALLED_APPS` — the local app may need to be added for changes to take effect.
- `db.sqlite3` is checked in; migrations may already be applied. Inspect `chess_analyzer/ChessAnalyzer/migrations/` before creating new migrations.
- `DEBUG = True` and a repo-committed `SECRET_KEY` are present in `settings.py` (development-only). Do not attempt to rotate or publish secrets here unless instructed.
- README.md is outdated (mentions Python 3.4 and IntelliJ). Prefer reading `settings.py` and `manage.py` for actual runtime expectations.

## Integration points and dependencies
- No external services or third-party integrations are referenced in code (no API client configs, no Celery, no external DB). Dependencies are not declared in a `requirements.txt` — assume a matching Django version (5.1.7) and standard Python stdlib unless a PR adds others.

## How to make safe edits (rules for AI agents)
- Small, focused changes only: update a single file or a coherent set (e.g., models + migrations). Keep diffs minimal.
- If you change models, generate migrations (`makemigrations`) and include the migration files in the change.
- When touching `settings.py`, explicitly mention risk (SECRET_KEY, DEBUG) and avoid publishing alternate secrets.
- Prefer adding the local app to `INSTALLED_APPS` by inserting the app config string from `ChessAnalyzer/apps.py` rather than guessing.

## Examples (quick pointers)
- Add a new model: edit `chess_analyzer/ChessAnalyzer/models.py`, then run `makemigrations` and `migrate` for that app.
- Register admin models: update `chess_analyzer/ChessAnalyzer/admin.py` and confirm the admin shows at `/admin/` after creating a superuser.

## When you need more info
- Ask the repository owner for the intended target Python version and any missing dependency versions (there's no `requirements.txt`).

---
Please review this instruction file and tell me if you'd like the agent to be more conservative (only suggest changes) or more proactive (create migrations, tests, and run the server locally).  
