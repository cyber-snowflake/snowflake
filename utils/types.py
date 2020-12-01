from dataclasses import dataclass, fields
from typing import Optional

from discord import AllowedMentions


@dataclass
class Mention:
    nobody: AllowedMentions = AllowedMentions(everyone=False, users=False, roles=False)
    user: AllowedMentions = AllowedMentions(everyone=False, users=True, roles=False)
    role: AllowedMentions = AllowedMentions(everyone=False, users=False, roles=True)


class Reminder:
    def __init__(self, *, data):
        self.id = data["id"]
        self.user_id = data["user_id"]
        self.created_at = data["created_at"]
        self.trigger_at = data["trigger_at"]
        self.initiator_message_url = data["initiator_message_url"]
        self.content = data["content"]

    def __eq__(self, other):
        try:
            return self.id == other.id
        except:
            return False

    def __repr__(self):
        return "<Action id={0.id} user_id={0.user_id} trigger_at={0.trigger_at}>".format(self)


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
