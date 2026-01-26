---
description: How to use Alembic for database migrations
---

# Alembic Usage Guide

## 1. Create a New Migration (Generate Script)

When you modify your SQLAlchemy models (e.g., adding a column in `model.py`), run this command to generate a migration script automatically.

```bash
.venv/bin/alembic revision --autogenerate -m "your message here"
```

_Example: `.venv/bin/alembic revision --autogenerate -m "add expires_at column"`_

## 2. Review the Migration Script

Alaways check the new file created in `alembic/versions/`. It should contain `op.add_column`, `op.create_table`, etc.

## 3. Apply Migrations (Upgrade)

To apply the changes to your actual database:

```bash
.venv/bin/alembic upgrade head
```

## 4. Revert Migrations (Downgrade)

To undo the last migration (e.g., if something went wrong):

```bash
.venv/bin/alembic downgrade -1
```

## Common Issues

- **Command not found**: Make sure to use the path to the binary in your virtual environment (`.venv/bin/alembic`).
- **No changes detected**: Ensure your new model is imported in `src/database/models.py` so Alembic "sees" it.
