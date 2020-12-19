from dataclasses import dataclass


# noinspection DuplicatedCode
@dataclass(frozen=True)
class Postgres:
    user = "postgres"
    password = "postgres"
    database = "bot"
    host = "localhost"
    port = 5432
    dsn = f"postgresql://{user}:{password}@{host}:{port}/{database}"


# noinspection DuplicatedCode
@dataclass(frozen=True)
class Bot:
    owner_id = 123123
    default_prefix = "!"
    token = "Nzas2Ksakjjksdllkdgsjlsdkgkdlfgljkdfjkglk23r"
    shard_count = 1
    shard_ids = [0]
    support_guild_id = 123123123123
    imgur_id = "client-id"
