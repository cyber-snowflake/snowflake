import asyncio
import logging
import sys
from os import environ
from os.path import dirname

import click
import matplotlib
from loguru import logger

import config
from bot import BigMommy
from src.loguru_intercept import InterceptHandler
from src.sql import psql

try:
    import uvloop
except ImportError:
    if sys.platform == "win32":
        _loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(_loop)
    logger.warning(
        " ================================\n",
        "=   UVLOOP PACKAGE NOT FOUND   =\n",
        "= DEFAULT EVENT POLICY APPLIED =\n",
        "================================\n",
    )
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    logger.info(
        " ===============================\n",
        "= UVLOOP EVENT POLICY APPLIED =\n",
        "===============================\n",
    )

ROOT = dirname(__file__)


def setup_logging():
    l = logging.getLogger()
    l.setLevel(environ.get("LOGGING_LEVEL", "INFO"))
    l.handlers = [InterceptHandler()]

    logger.remove()
    logger.add(sys.stderr, enqueue=True)


def start_bot():
    matplotlib.use("Agg")
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(psql().connect(config.Postgres.dsn))
    except Exception as e:
        click.echo(f"Failed to connect to the PostgreSQL\n----------\n{e}", file=sys.stderr)
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
