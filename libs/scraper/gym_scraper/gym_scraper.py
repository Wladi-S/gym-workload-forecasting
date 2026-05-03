import os
from collections.abc import Callable, Mapping, Sequence
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any, cast
from zoneinfo import ZoneInfo

import requests

BERLIN = ZoneInfo("Europe/Berlin")
REQUEST_TIMEOUT_SECONDS = 15

GYM_IDS: tuple[int, ...] = (1, 7, 11, 12, 13, 20, 21, 23, 24, 33, 34, 37, 38, 41)

type DbConfig = dict[str, str | int]
type Reading = tuple[int, Decimal, datetime]
type Clock = Callable[[], datetime]
type Fetcher = Callable[[int, str], Mapping[str, object]]


def _environment(environ: Mapping[str, str] | None) -> Mapping[str, str]:
    return os.environ if environ is None else environ


def _required_env(name: str, environ: Mapping[str, str]) -> str:
    value = environ.get(name)
    if value is None or value == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _env_port(name: str, environ: Mapping[str, str]) -> int:
    raw_port = environ.get(name) or "5432"
    try:
        return int(raw_port)
    except ValueError as exc:
        raise RuntimeError(f"Invalid integer environment variable: {name}") from exc


def build_db_config(
    prefix: str,
    environ: Mapping[str, str] | None = None,
    *,
    default_sslmode: str | None = None,
) -> DbConfig:
    env = _environment(environ)
    config: DbConfig = {
        "host": _required_env(f"{prefix}__HOST", env),
        "port": _env_port(f"{prefix}__PORT", env),
        "dbname": _required_env(f"{prefix}__NAME", env),
        "user": _required_env(f"{prefix}__USER", env),
        "password": _required_env(f"{prefix}__PASSWORD", env),
    }

    sslmode = env.get(f"{prefix}__SSLMODE") or default_sslmode
    if sslmode is not None:
        config["sslmode"] = sslmode

    return config


def get_data(gym_id: int, mandant: str) -> dict[str, object]:
    params: dict[str, str | int] = {
        "mandant": mandant,
        "stud_nr": gym_id,
        "jsonResponse": "1",
    }
    response = requests.get(
        "https://portal.aidoo-online.de/workload",
        params=params,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()

    payload: Any = response.json()
    if not isinstance(payload, dict):
        raise ValueError("Expected JSON object from workload endpoint")

    return cast(dict[str, object], payload)


def parse_workload(data: Mapping[str, object]) -> Decimal:
    try:
        workload = Decimal(str(data["numval"]))
    except InvalidOperation as exc:
        raise ValueError("Invalid numval in workload response") from exc

    if not workload.is_finite():
        raise ValueError("Invalid numval in workload response")

    return workload


def now_berlin() -> datetime:
    return datetime.now(BERLIN)


def collect_readings(
    *,
    mandant: str,
    gym_ids: Sequence[int] = GYM_IDS,
    fetch: Fetcher = get_data,
    clock: Clock = now_berlin,
) -> list[Reading]:
    recorded_at = clock()
    readings: list[Reading] = []

    for gym_id in gym_ids:
        try:
            workload_new = parse_workload(fetch(gym_id, mandant))
        except (KeyError, TypeError, ValueError, requests.RequestException):
            continue

        readings.append((gym_id, workload_new, recorded_at))

    return readings
