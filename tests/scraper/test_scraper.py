from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest
import requests
from gym_scraper import gym_scraper as scraper

BERLIN = ZoneInfo("Europe/Berlin")


def complete_env() -> dict[str, str]:
    return {
        "SCRAPER_MANDANT": "test_mandant",
        "SCRAPER_LOCAL_DB__HOST": "local-host",
        "SCRAPER_LOCAL_DB__PORT": "5433",
        "SCRAPER_LOCAL_DB__NAME": "local-db",
        "SCRAPER_LOCAL_DB__USER": "local-user",
        "SCRAPER_LOCAL_DB__PASSWORD": "local-secret",
        "SCRAPER_SUPABASE_DB__HOST": "supabase-host",
        "SCRAPER_SUPABASE_DB__PORT": "6543",
        "SCRAPER_SUPABASE_DB__NAME": "supabase-db",
        "SCRAPER_SUPABASE_DB__USER": "supabase-user",
        "SCRAPER_SUPABASE_DB__PASSWORD": "supabase-secret",
        "SCRAPER_SUPABASE_DB__SSLMODE": "require",
    }


def test_build_db_config_reads_values_from_environment() -> None:
    config = scraper.build_db_config("SCRAPER_LOCAL_DB", complete_env())

    assert config == {
        "host": "local-host",
        "port": 5433,
        "dbname": "local-db",
        "user": "local-user",
        "password": "local-secret",
    }


def test_build_db_config_requires_missing_values() -> None:
    with pytest.raises(RuntimeError, match="SCRAPER_LOCAL_DB__HOST"):
        scraper.build_db_config("SCRAPER_LOCAL_DB", {})


def test_collect_readings_skips_failed_studio_and_keeps_successes() -> None:
    recorded_at = datetime(2026, 5, 3, 12, 30, tzinfo=BERLIN)
    requested_gym_ids: list[int] = []

    def fetch(gym_id: int, mandant: str) -> dict[str, object]:
        requested_gym_ids.append(gym_id)
        assert mandant == "test_mandant"
        if gym_id == 7:
            raise requests.RequestException("timeout")
        return {"numval": str(gym_id)}

    readings = scraper.collect_readings(
        mandant="test_mandant",
        gym_ids=[1, 7, 11],
        fetch=fetch,
        clock=lambda: recorded_at,
    )

    assert requested_gym_ids == [1, 7, 11]
    assert readings == [
        (1, Decimal("1"), recorded_at),
        (11, Decimal("11"), recorded_at),
    ]


def test_collect_readings_skips_invalid_numval_payloads() -> None:
    recorded_at = datetime(2026, 5, 3, 12, 30, tzinfo=BERLIN)

    def fetch(gym_id: int, _mandant: str) -> dict[str, object]:
        payloads: dict[int, dict[str, object]] = {
            1: {"numval": "not-a-number"},
            7: {},
            11: {"numval": "42.5"},
        }
        return payloads[gym_id]

    readings = scraper.collect_readings(
        mandant="test_mandant",
        gym_ids=[1, 7, 11],
        fetch=fetch,
        clock=lambda: recorded_at,
    )

    assert readings == [(11, Decimal("42.5"), recorded_at)]
