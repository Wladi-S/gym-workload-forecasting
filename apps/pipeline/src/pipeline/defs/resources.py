import os

import dagster as dg
import psycopg


class PostgresResource(dg.ConfigurableResource):
    """Connection for shared PostgreSQL database."""

    host: str
    port: int
    dbname: str
    user: str
    password: str

    def get_connection(self):
        return psycopg.connect(
            host=self.host,
            port=self.port,
            dbname=self.dbname,
            user=self.user,
            password=self.password,
        )


@dg.definitions
def postgres_resources():
    return dg.Definitions(
        resources={
            "postgres": PostgresResource(
                host=os.getenv("HOST"),
                port=int(os.getenv("PORT")),
                dbname=os.getenv("DBNAME"),
                user=os.getenv("DBUSER"),
                password=os.getenv("PASSWORD"),
            ),
        },
    )
