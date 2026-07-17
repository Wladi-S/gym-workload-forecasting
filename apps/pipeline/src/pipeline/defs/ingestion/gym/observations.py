import dagster as dg
from pipeline.defs.resources import PostgresResource

from .resources import GymApiResource
from .scraper import run_scraper


@dg.asset(
    group_name="ingestion",
    kinds={"postgres", "python"},
    tags={"domain": "gym", "layer": "raw"},
    pool="gym_ingestion",
)
def gym_observations(
    context: dg.AssetExecutionContext,
    gym_api: GymApiResource,
    postgres: PostgresResource,
):
    """Raw gym workload observations fetched from API and stored in PostgreSQL."""
    result = run_scraper(gym_api, postgres)

    for gym_id in result.failed_gym_ids:
        context.log.warning("Abruf für Studio %s fehlgeschlagen", gym_id)

    return dg.MaterializeResult(
        metadata={
            "successful_studios": result.successful,
            "failed_studios": result.failed,
            "failed_gym_ids": result.failed_gym_ids,
            "inserted_rows": result.inserted,
        }
    )


gym_scraping_schedule = dg.ScheduleDefinition(
    name="gym_scraping_every_minute",
    target=gym_observations,
    cron_schedule="* * * * *",
    execution_timezone="Europe/Berlin",
)
