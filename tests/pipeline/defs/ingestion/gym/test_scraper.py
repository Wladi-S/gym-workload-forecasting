from datetime import UTC, datetime

import requests
from pipeline.defs.ingestion.gym.scraper import collect_readings


def test_collect_readings_keeps_successes_and_reports_failures() -> None:
    recorded_at = datetime(2026, 7, 15, 12, 30, tzinfo=UTC)
    requested_gym_ids: list[int] = []

    def fetch_workload(gym_id: int) -> float:
        requested_gym_ids.append(gym_id)
        if gym_id == 7:
            raise requests.Timeout("timed out")
        return float(gym_id)

    readings, failed_gym_ids = collect_readings(
        [1, 7, 11],
        fetch_workload=fetch_workload,
        clock=lambda: recorded_at,
    )

    assert requested_gym_ids == [1, 7, 11]
    assert readings == [(1, 1.0, recorded_at), (11, 11.0, recorded_at)]
    assert failed_gym_ids == [7]
