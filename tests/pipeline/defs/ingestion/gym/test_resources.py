from unittest.mock import Mock, patch

import pytest
import requests
from pipeline.defs.ingestion.gym.resources import GymApiResource


def test_fetch_workload_requests_configured_gym() -> None:
    response = Mock(spec=requests.Response)
    response.json.return_value = {"numval": "22.73"}
    resource = GymApiResource(
        mandant="test_mandant",
        base_url="https://example.test/",
        timeout_seconds=2.5,
    )

    with patch(
        "pipeline.defs.ingestion.gym.resources.requests.get",
        return_value=response,
    ) as request:
        workload = resource.fetch_workload(13)

    assert workload == 22.73
    request.assert_called_once_with(
        "https://example.test/workload",
        params={
            "mandant": "test_mandant",
            "stud_nr": 13,
            "jsonResponse": "1",
        },
        timeout=2.5,
    )
    response.raise_for_status.assert_called_once_with()


@pytest.mark.parametrize(
    "payload",
    [
        [],
        {},
        {"numval": None},
        {"numval": "not-a-number"},
        {"numval": "nan"},
    ],
)
def test_fetch_workload_rejects_invalid_payload(payload: object) -> None:
    response = Mock(spec=requests.Response)
    response.json.return_value = payload
    resource = GymApiResource(mandant="test_mandant")

    with (
        patch(
            "pipeline.defs.ingestion.gym.resources.requests.get",
            return_value=response,
        ),
        pytest.raises(ValueError, match="Invalid workload response"),
    ):
        resource.fetch_workload(13)
