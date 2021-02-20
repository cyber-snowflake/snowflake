#  Copyright (c) 2020 — present, moretzu (モーレツ)
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

from tomodachi.core.exceptions import GloballyRateLimited


async def spam_control(ctx):
    bucket = ctx.bot.global_rate_limit.get_bucket(ctx.message)
    retry_after = bucket.update_rate_limit()

    if retry_after:
        raise GloballyRateLimited(ctx.author, retry_after)

    return True
