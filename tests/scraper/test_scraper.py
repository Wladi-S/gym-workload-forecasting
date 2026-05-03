import pytest
from gym_scraper import gym_scraper as scraper


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
