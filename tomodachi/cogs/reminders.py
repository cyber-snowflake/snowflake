#  Most of the code in this file was used from RoboDanny's source code and modified.
# I'm struggling with asyncio a lot but I want to provide stable and working system :(
#
# Also I commented here a bit just to be able to understand the code in a future.
# Hopefully, my thoughts and my understanding is at least close to the reality.
#
#                           RoboDanny is ♥️
#
# Sources: https://github.com/Rapptz/RoboDanny/blob/f76f50d340d095113538d0b10ce5251001b42025/cogs/reminder.py

import asyncio
import random
from datetime import datetime
from datetime import timedelta
from typing import Optional

import arrow
from asyncpg import PostgresConnectionError
from discord import ConnectionClosed, Forbidden
from discord.ext import commands
from discord.ext.menus import MenuPages

from tomodachi.core import Tomodachi
from tomodachi.src.myembed import MyEmbed
from tomodachi.src.mymenus import MyPagesSource
from tomodachi.utils import TimeInput


class Reminder:
    __slots__ = ("id", "user_id", "created_at", "trigger_at", "initiator_message_url", "content")

    def __init__(self, *, data):
        self.id: int = data["id"]
        self.user_id: int = data["user_id"]
        self.created_at: datetime = data["created_at"]
        self.trigger_at: datetime = data["trigger_at"]
        self.initiator_message_url: str = data["initiator_message_url"]
        self.content: str = data["content"]

    def __eq__(self, other):
        try:
            return self.id == other.id
        except:
            return False

    def __repr__(self):
        return "<Reminder id={0.id} user_id={0.user_id} trigger_at={0.trigger_at}>".format(self)


class Reminders(commands.Cog):
    def __init__(self, bot: Tomodachi):
        self.bot = bot
        self.action_event = asyncio.Event()
        self.current_action: Optional[Reminder] = None
        self.task = bot.loop.create_task(self.dispatch_actions())

    def cog_unload(self):
        self.task.cancel()

    @commands.Cog.listener()
    async def on_action_complete(self, action: Reminder):
        user = self.bot.get_user(action.user_id)
        if user:
            e = MyEmbed(title="Reminder", timestamp=True)

            e.description = action.content
            e.add_field(
                name="Source Message",
                value=f"[Jump to Message]({action.initiator_message_url})",
            )

            try:
                await user.send(
                    f"You asked me {arrow.get(action.created_at).humanize()} to remind you about this!",
                    embed=e,
                )
            except Forbidden:
                pass

    async def get_active_action(self, days: int = 7):
        query = "SELECT * FROM reminders WHERE trigger_at < (current_date + $1::interval) ORDER BY trigger_at LIMIT 1;"

        async with self.bot.pg.pool.acquire() as conn:
            record = await conn.fetchrow(query, timedelta(days=days))

        if record:
            return Reminder(data=record)
        else:
            return None

    async def wait_for_active_action(self, days: int = 7):
        action = await self.get_active_action(days=days)
        if action is not None:
            # Whenever a new active action is found the action event will set to true
            self.action_event.set()
            return action

        # In other cases action event reset along with currently active action
        self.action_event.clear()
        self.current_action = None
        # Waiting for the action event to be set to true (will happen once some action is found)
        await self.action_event.wait()
        return await self.get_active_action(days=days)

    async def execute_action(self, action: Reminder):
        # We should delete an action from database before executing it
        await self.bot.pg.pool.execute("DELETE FROM reminders WHERE id = $1;", action.id)
        self.bot.dispatch("action_complete", action)

    async def dispatch_actions(self):
        try:
            while not self.bot.is_closed():
                # asyncio's sleep works reliably only up to 48 days, so we're searching for 40 days old actions
                action = self.current_action = await self.wait_for_active_action(days=40)
                now = arrow.utcnow().naive

                # If the action trigger time is now or not now, we sleep (sometimes you gotta rest you know)
                if action.trigger_at >= now:
                    to_sleep = (action.trigger_at - now).total_seconds()
                    await asyncio.sleep(to_sleep)

                # In other cases just proceed to the execution
                await self.execute_action(action)
        except asyncio.CancelledError:
            raise
        except (OSError, ConnectionClosed, PostgresConnectionError):
            self.task.cancel()
            self.task = self.bot.loop.create_task(self.dispatch_actions())

    async def create_short_action(self, seconds, action: Reminder):
        await asyncio.sleep(seconds)
        self.bot.dispatch("action_complete", action)

    async def create_action(self, *, user_id: int, trigger_at, initiator_message_url: str, content: str):
        now = arrow.utcnow().naive

        action = Reminder(
            data={
                "id": random.randint(0, 100000),
                "user_id": user_id,
                "created_at": now,
                "trigger_at": trigger_at,
                "initiator_message_url": initiator_message_url,
                "content": content,
            }
        )

        delta = (trigger_at - now).total_seconds()
        if delta <= 60:
            self.bot.loop.create_task(self.create_short_action(delta, action))
            return action

        else:
            query = (
                "INSERT INTO reminders (user_id, created_at, trigger_at, initiator_message_url, content) "
                "VALUES ($1, $2, $3, $4, $5) RETURNING id;"
            )

            async with self.bot.pg.pool.acquire() as conn:
                action_id = await conn.fetchval(query, user_id, now, trigger_at, initiator_message_url, content)
            action.id = action_id

            if delta <= 3456000:  # 40 days
                # If the time delta is lower or is 40 days the action event must be set to true
                self.action_event.set()

            if self.current_action and trigger_at < self.current_action.trigger_at:
                self.task.cancel()
                self.task = self.bot.loop.create_task(self.dispatch_actions())

            return action

    @commands.group(aliases=("r", "reminders"))
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def reminder(self, ctx: commands.Context):
        if not ctx.invoked_subcommand:
            await ctx.send(":x: You haven't used any subcommand, please, see help.")

    @reminder.command(aliases=("create",))
    async def add(self, ctx: commands.Context, to_wait: TimeInput, *, text: str):
        trigger_moment = arrow.utcnow().naive + to_wait
        await self.create_action(
            user_id=ctx.author.id,
            trigger_at=trigger_moment,
            initiator_message_url=ctx.message.jump_url,
            content=text,
        )

        await ctx.send(f":ok_hand: I will remind you about it {arrow.get(trigger_moment).humanize()}")

    @reminder.command(aliases=("ls",))
    async def list(self, ctx: commands.Context):
        rows = await self.bot.pg.pool.fetch(
            "SELECT * FROM reminders WHERE user_id = $1 ORDER BY trigger_at;", ctx.author.id
        )

        if not rows:
            return await ctx.send(":x: You don't have any reminders set.")

        actions = (Reminder(data=dict(row)) for row in rows)
        entries = [f"**(ID: {action.id})** {arrow.get(action.trigger_at).humanize()}" for action in actions]

        src = MyPagesSource(entries, per_page=5, title=f"{self.bot.my_emojis.slowmode} Reminders List")
        menu = MenuPages(src, clear_reactions_after=True)

        await menu.start(ctx)

    @reminder.command(aliases=("del", "remove", "rmv"))
    async def delete(self, ctx: commands.Context, reminder_id: int):
        query = "DELETE FROM reminders WHERE id = $1 AND user_id = $2 RETURNING true;"
        execution = await self.bot.pg.pool.fetchval(query, reminder_id, ctx.author.id)

        if execution is True:
            await ctx.send(f":ok_hand: You have successfully deleted **#{reminder_id}** reminder.")
        else:
            await ctx.send(":x: You tried to delete non-existing or someone else's reminder.")

    @reminder.command(aliases=("clean",))
    async def clear(self, ctx: commands.Context):
        query = "DELETE FROM reminders WHERE user_id = $1 RETURNING true;"
        execution = await self.bot.pg.pool.fetchval(query, ctx.author.id)

        if execution is True:
            await ctx.send(":ok_hand: You have successfully cleared your reminders list.")
        else:
            await ctx.send(":x: You don't have any reminders.")


def setup(bot):
    bot.add_cog(Reminders(bot))
