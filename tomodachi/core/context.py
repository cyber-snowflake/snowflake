#  Copyright (c) 2020 — present, moretzu (モーレツ)
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

from discord.ext import commands

from tomodachi.core.bot import Tomodachi


class TomodachiContext(commands.Context):
    bot: Tomodachi
