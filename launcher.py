import asyncio
import importlib
import logging
import sys
from os import environ
from os.path import dirname

import click
import matplotlib
from loguru import logger

import configurator as config
from bot import BigMommy
from src.loguru_intercept import InterceptHandler
from utils import cachemanager, psql

try:
    uvloop = importlib.import_module("uvloop")
except ImportError:
    logger.warning(f"uvloop package not found, used {asyncio.get_event_loop_policy()} policy")
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    logger.info("uvloop policy was applied")

ROOT = dirname(__file__)


def setup_logging():
    logging_level = environ.get("LOGGING_LEVEL", "INFO")

    std_logger = logging.getLogger()
    std_logger.setLevel(logging_level)
    std_logger.handlers = [InterceptHandler()]

    logger.remove()
    logger.add(sys.stderr, enqueue=True, level=logging_level)


def start_bot():
    matplotlib.use("Agg")
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(psql().connect(config.postgres_config.dsn))
    except Exception as e:
        click.echo(f"Failed to connect to the PostgreSQL\n----------\n{e}", file=sys.stderr)
        return

    try:
        loop.run_until_complete(cachemanager().connect_redis(config.redis_config.uri))
    except Exception as e:
        click.echo(f"Failed to connect to the Redis\n----------\n{e}", file=sys.stderr)
        return

    bot = BigMommy()
    logger.debug("Bot instance created.")

    environ["JISHAKU_HIDE"] = "True"
    bot.load_extension("jishaku")
    bot.run()


@click.command()
@click.pass_context
def main(ctx):
    if ctx.invoked_subcommand is None:
        setup_logging()
        start_bot()


if __name__ == "__main__":
    main()
