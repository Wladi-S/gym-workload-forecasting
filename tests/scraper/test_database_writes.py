import os
from collections.abc import Iterator, Mapping
from datetime import datetime
from decimal import Decimal
from typing import Any, cast
from zoneinfo import ZoneInfo

import psycopg
import pytest
from gym_scraper import gym_scraper as scraper

pytestmark = pytest.mark.db

BERLIN = ZoneInfo("Europe/Berlin")


def _db_config(environ: Mapping[str, str] | None = None) -> scraper.DbConfig:
    env = os.environ if environ is None else environ
    return {
        "host": env.get("TEST_DB_HOST", "127.0.0.1"),
        "port": int(env.get("TEST_DB_PORT", "55432")),
        "dbname": env.get("TEST_DB_NAME", "gym_workload_test"),
        "user": env.get("TEST_DB_USER", "gym_workload_test"),
        "password": env.get("TEST_DB_PASSWORD", "gym_workload_test"),
    }


def _scraper_env() -> dict[str, str]:
    config = _db_config()
    return {
        "SCRAPER_MANDANT": "test_mandant",
        "SCRAPER_LOCAL_DB__HOST": str(config["host"]),
        "SCRAPER_LOCAL_DB__PORT": str(config["port"]),
        "SCRAPER_LOCAL_DB__NAME": str(config["dbname"]),
        "SCRAPER_LOCAL_DB__USER": str(config["user"]),
        "SCRAPER_LOCAL_DB__PASSWORD": str(config["password"]),
    }


@pytest.fixture(autouse=True)
def clean_data_table() -> Iterator[None]:
    with psycopg.connect(**cast(Any, _db_config())) as conn, conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE public.data;")

    yield

    with psycopg.connect(**cast(Any, _db_config())) as conn, conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE public.data;")


def _data_rows() -> list[tuple[int, Decimal, datetime]]:
    with psycopg.connect(**cast(Any, _db_config())) as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT gym_id, workload, recorded_at
            FROM public.data
            ORDER BY gym_id, recorded_at;
            """,
        )
        rows = cur.fetchall()

    return [
        (cast(int, gym_id), cast(Decimal, workload), cast(datetime, recorded_at))
        for gym_id, workload, recorded_at in rows
    ]


def test_write_readings_inserts_first_reading_when_no_previous_data_exists() -> None:
    recorded_at = datetime(2026, 5, 6, 14, 53, tzinfo=BERLIN)

    scraper.write_readings(
        _db_config(),
        [(1, Decimal("34.17"), recorded_at)],
        "test database",
    )

    assert _data_rows() == [(1, Decimal("34.17"), recorded_at)]


def test_write_readings_does_not_duplicate_unchanged_latest_workload() -> None:
    first_seen_at = datetime(2026, 5, 6, 14, 53, tzinfo=BERLIN)
    second_seen_at = datetime(2026, 5, 6, 14, 58, tzinfo=BERLIN)

    scraper.write_readings(
        _db_config(),
        [(1, Decimal("34.17"), first_seen_at)],
        "test database",
    )
    scraper.write_readings(
        _db_config(),
        [(1, Decimal("34.17"), second_seen_at)],
        "test database",
    )

    assert _data_rows() == [(1, Decimal("34.17"), first_seen_at)]


def test_write_readings_inserts_changed_latest_workload() -> None:
    first_seen_at = datetime(2026, 5, 6, 14, 53, tzinfo=BERLIN)
    second_seen_at = datetime(2026, 5, 6, 14, 58, tzinfo=BERLIN)

    scraper.write_readings(
        _db_config(),
        [(1, Decimal("34.17"), first_seen_at)],
        "test database",
    )
    scraper.write_readings(
        _db_config(),
        [(1, Decimal("34.52"), second_seen_at)],
        "test database",
    )

    assert _data_rows() == [
        (1, Decimal("34.17"), first_seen_at),
        (1, Decimal("34.52"), second_seen_at),
    ]


def test_write_readings_persists_raw_workload_values_without_range_validation() -> None:
    recorded_at = datetime(2026, 5, 6, 14, 53, tzinfo=BERLIN)

    scraper.write_readings(
        _db_config(),
        [(1, Decimal("101.25"), recorded_at)],
        "test database",
    )

    assert _data_rows() == [(1, Decimal("101.25"), recorded_at)]


def test_write_readings_rejects_reading_for_unknown_gym_id() -> None:
    recorded_at = datetime(2026, 5, 6, 14, 53, tzinfo=BERLIN)

    with pytest.raises(psycopg.errors.ForeignKeyViolation):
        scraper.write_readings(
            _db_config(),
            [(99, Decimal("42.00"), recorded_at)],
            "test database",
        )

    assert _data_rows() == []


def test_main_writes_collected_readings_to_test_database() -> None:
    recorded_at = datetime(2026, 5, 6, 14, 53, tzinfo=BERLIN)

    def fetch(gym_id: int, mandant: str) -> dict[str, object]:
        assert mandant == "test_mandant"
        workloads = {
            1: "34.17",
            7: "60.25",
        }
        return {"numval": workloads[gym_id]}

    scraper.main(
        environ=_scraper_env(),
        fetch=fetch,
        gym_ids=[1, 7],
        clock=lambda: recorded_at,
    )

    assert _data_rows() == [
        (1, Decimal("34.17"), recorded_at),
        (7, Decimal("60.25"), recorded_at),
    ]
