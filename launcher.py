import asyncio
import logging
import sys
from os import environ
from os.path import dirname

import click
import matplotlib

import config
from bot import BigMommy
from src.sql import psql

try:
    import uvloop
except ImportError:
    if sys.platform == "win32":
        _loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(_loop)
    print(
        " ================================\n",
        "=   UVLOOP PACKAGE NOT FOUND   =\n",
        "= DEFAULT EVENT POLICY APPLIED =\n",
        "================================\n",
    )
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    print(
        " ===============================\n",
        "= UVLOOP EVENT POLICY APPLIED =\n",
        "===============================\n",
    )

ROOT = dirname(__file__)


def setup_logging():
    logging.basicConfig(level=logging.INFO)


def start_bot():
    matplotlib.use("Agg")
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(psql().connect(config.Postgres.dsn))
    except Exception as e:
        click.echo(f"Failed to connect to the PostgreSQL\n----------\n{e}", file=sys.stderr)
        return

    bot = BigMommy()
    print("Bot instance created.")

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
