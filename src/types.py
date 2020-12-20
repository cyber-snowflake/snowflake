from dataclasses import dataclass, fields
from datetime import datetime
from typing import Optional

from discord import AllowedMentions


@dataclass
class Mention:
    nobody = AllowedMentions(everyone=False, users=False, roles=False, replied_user=False)
    user = AllowedMentions(everyone=False, users=True, roles=False)
    role = AllowedMentions(everyone=False, users=False, roles=True)


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


@dataclass(init=False)
class GuildSettings:
    prefix: Optional[str]
    main_vc_id: Optional[int]
    tz: str = "UTC"

    def __init__(self, **kwargs):
        names = set([f.name for f in fields(self)])
        for k, v in kwargs.items():
            if k in names:
                setattr(self, k, v)

    def __repr__(self):
        return "<GuildSettings {0}>".format(" ".join("{}={!r}".format(k, v) for k, v in self.__dict__.items()))
