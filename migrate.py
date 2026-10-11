import os
from pathlib import Path

import psycopg


MIGRATIONS_DIR = Path(__file__).parent / "migrations"


def main() -> None:
    migrations = sorted(MIGRATIONS_DIR.glob("*.sql"))
    if not migrations:
        print(f"[MIGRATE] No SQL migrations found in {MIGRATIONS_DIR}")
        return

    with psycopg.connect(os.environ["DATABASE_URL"]) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                name TEXT PRIMARY KEY,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
        applied = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM schema_migrations"
            ).fetchall()
        }

        for migration in migrations:
            if migration.name in applied:
                print(f"[MIGRATE] Skipping already applied migration {migration.name}")
                continue

            print(f"[MIGRATE] Applying migration {migration.name}")
            connection.execute(migration.read_text(encoding="utf-8"))
            connection.execute(
                "INSERT INTO schema_migrations (name) VALUES (%s)",
                (migration.name,),
            )


if __name__ == "__main__":
    main()
