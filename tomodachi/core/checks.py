#  Copyright (c) 2020 — present, moretzu (モーレツ)
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

from __future__ import annotations

from typing import TYPE_CHECKING

from tomodachi.core.exceptions import GloballyRateLimited

if TYPE_CHECKING:
    from tomodachi.core.context import TomodachiContext


async def spam_control(ctx: TomodachiContext):
    if not ctx.bot.owner_has_limits and ctx.message.author.id == ctx.bot.owner_id:
        return True

    bucket = ctx.bot.global_rate_limit.get_bucket(ctx.message)
    retry_after = bucket.update_rate_limit()

    if retry_after:
        raise GloballyRateLimited(ctx.author, retry_after)

    return True
