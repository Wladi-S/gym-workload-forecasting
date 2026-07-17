from dataclasses import dataclass
from datetime import UTC, datetime

import requests
from pipeline.defs.resources import PostgresResource

from .resources import GymApiResource

GYM_IDS = (
    1,
    7,
    11,
    12,
    13,
    20,
    21,
    23,
    24,
    33,
    34,
    37,
    38,
    41,
)

SQL_INSERT_IF_CHANGED = """
INSERT INTO public.data (gym_id, workload, recorded_at)
SELECT %s, %s, %s
WHERE %s IS DISTINCT FROM (
    SELECT workload
    FROM public.data
    WHERE gym_id = %s
    ORDER BY recorded_at DESC
    LIMIT 1
);
"""


@dataclass(frozen=True)
class ScrapeResults:
    successful: int
    failed: int
    failed_gym_ids: list[int]
    inserted: int


def utc_now() -> datetime:
    return datetime.now(UTC)


def collect_readings(
    gym_ids,
    *,
    fetch_workload,
    clock=utc_now,
):
    recorded_at = clock()
    readings = []
    failed_gym_ids = []

    for gym_id in gym_ids:
        try:
            workload = fetch_workload(gym_id)
        except (ValueError, requests.RequestException):
            failed_gym_ids.append(gym_id)
            continue

        readings.append((gym_id, workload, recorded_at))

    return readings, failed_gym_ids


def write_readings(postgres: PostgresResource, readings) -> int:
    inserted = 0

    with (
        postgres.get_connection() as connection,
        connection.cursor() as cursor,
    ):
        for gym_id, workload, recorded_at in readings:
            cursor.execute(
                SQL_INSERT_IF_CHANGED,
                (
                    gym_id,
                    workload,
                    recorded_at,
                    workload,
                    gym_id,
                ),
            )
            inserted += cursor.rowcount

    return inserted


def run_scraper(gym_api: GymApiResource, postgres: PostgresResource):

    readings, failed_gym_ids = collect_readings(
        GYM_IDS,
        fetch_workload=gym_api.fetch_workload,
    )

    if not readings:
        raise RuntimeError("All gym requests failed")

    inserted = write_readings(postgres, readings)

    return ScrapeResults(
        successful=len(readings),
        failed=len(failed_gym_ids),
        failed_gym_ids=failed_gym_ids,
        inserted=inserted,
    )
