import math
import os

import dagster as dg
import requests


class GymApiResource(dg.ConfigurableResource):
    """Client for the external gym workload API."""

    mandant: str
    base_url: str = "https://portal.aidoo-online.de"
    timeout_seconds: float = 5.0

    def fetch_workload(self, gym_id: int) -> float:
        params: dict[str, str | int] = {
            "mandant": self.mandant,
            "stud_nr": gym_id,
            "jsonResponse": "1",
        }
        response = requests.get(
            f"{self.base_url.rstrip('/')}/workload",
            params=params,
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()

        payload: object = response.json()
        if not isinstance(payload, dict) or "numval" not in payload:
            raise ValueError("Invalid workload response")

        try:
            workload = float(payload["numval"])
        except (TypeError, ValueError) as error:
            raise ValueError("Invalid workload response") from error

        if not math.isfinite(workload):
            raise ValueError("Invalid workload response")

        return workload


@dg.definitions
def gym_resources() -> dg.Definitions:
    return dg.Definitions(
        resources={
            "gym_api": GymApiResource(
                mandant=os.getenv("MANDANT"),
            ),
        },
    )
