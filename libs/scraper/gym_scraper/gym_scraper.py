import os
from collections.abc import Mapping

type DbConfig = dict[str, str | int]


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
