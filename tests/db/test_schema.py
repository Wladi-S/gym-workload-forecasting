import os
from collections.abc import Mapping
from typing import Any, cast

import psycopg
import pytest

pytestmark = pytest.mark.db


def _db_config(environ: Mapping[str, str] | None = None) -> dict[str, str | int]:
    env = os.environ if environ is None else environ
    return {
        "host": env.get("TEST_DB_HOST", "127.0.0.1"),
        "port": int(env.get("TEST_DB_PORT", "55432")),
        "dbname": env.get("TEST_DB_NAME", "gym_workload_test"),
        "user": env.get("TEST_DB_USER", "gym_workload_test"),
        "password": env.get("TEST_DB_PASSWORD", "gym_workload_test"),
    }


def test_test_database_schema_is_initialized() -> None:
    with psycopg.connect(**cast(Any, _db_config())) as conn, conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM public.gym;")
        assert cur.fetchone() == (14,)

        cur.execute("SELECT count(*) FROM public.data;")
        assert cur.fetchone() == (0,)
