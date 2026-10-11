import os
import psycopg
from typing import Any
from psycopg.rows import dict_row


def connect() -> psycopg.Connection[dict[str, Any]]:
    return psycopg.connect(
        os.environ["DATABASE_URL"],
        connect_timeout=10,
        row_factory=dict_row,
    )