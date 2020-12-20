from discord.ext.commands.errors import CommandError


class BadCacheRequest(Exception):
    pass


class BlacklistedSnowflake(CommandError):
    pass


class NotInVoiceChat(CommandError):
    pass


class RoomNotFound(CommandError):
    pass
