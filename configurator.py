from os.path import dirname, join
from typing import Optional

import ujson
from discord import Colour

__all__ = ["bot_config", "redis_config", "postgres_config"]


class PostgresConfig:
    __slots__ = (
        "user",
        "password",
        "database",
        "host",
        "port",
    )

    def __init__(self, *args, **kwargs) -> None:
        self.user: str = kwargs.pop("user")
        self.password: str = kwargs.pop("password")
        self.database: str = kwargs.pop("database")
        self.host: str = kwargs.pop("host")
        self.port: int = int(kwargs.pop("port"))

    @property
    def dsn(self):
        return "postgresql://{0.user}:{0.password}@{0.host}:{0.port}/{0.database}".format(self)


class BotConfig:
    __slots__ = (
        "default_prefix",
        "_token",
        "_is_token_revealed",
        "shard_count",
        "shard_ids",
        "support_guild_id",
        "imgur_id",
        "_brand_color",
        "default_status",
        "default_emoji_id",
    )

    def __init__(self, *args, **kwargs) -> None:
        self.default_prefix: str = kwargs.pop("default_prefix")
        self._token: Optional[str] = kwargs.pop("token")
        self._is_token_revealed = False
        self.shard_count: int = kwargs.pop("shard_count")
        self.shard_ids: list[int] = kwargs.pop("shard_ids")
        self.support_guild_id: int = kwargs.pop("support_guild_id")
        self.imgur_id: str = kwargs.pop("imgur_id")
        self._brand_color = Colour.from_rgb(*kwargs.pop("brand_color"))
        self.default_status: str = kwargs.pop("default_status")
        self.default_emoji_id: int = kwargs.pop("default_emoji_id")

    @property
    def brand_color(self):
        return self._brand_color

    @property
    def token(self):
        if self._is_token_revealed:
            self._token = None

        self._is_token_revealed = True
        return self._token


class RedisConfig:
    __slots__ = ("uri",)

    def __init__(self, **kwargs) -> None:
        self.uri = kwargs.pop("uri")


with open(join(dirname(__file__), "./config.json"), "r", encoding="utf-8") as fp:
    _data = ujson.load(fp)

bot_config = BotConfig(**_data["BOT"])
postgres_config = PostgresConfig(**_data["POSTGRES"])
redis_config = RedisConfig(**_data["REDIS"])

del _data
