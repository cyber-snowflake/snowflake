from discord.ext.commands.errors import CommandError


class CacheMiss(Exception):
    pass


class CacheException(Exception):
    pass


class BlacklistedSnowflake(CommandError):
    pass


class NotInVoiceChat(CommandError):
    pass


class RoomNotFound(CommandError):
    pass


class InformUser(CommandError):
    """A way to communicate with a user in case of errors"""

    def __init__(self, message, *args, **kwargs):
        self.reply = kwargs.get("reply", False)
        self.message = message
        super().__init__(message=message, *args)
