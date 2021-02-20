#  Copyright (c) 2020 — present, moretzu (モーレツ)
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.


def make_progress_bar(position: float, total: float, *, length: int = 15, filler="█", emptiness=" ", in_brackets=False):
    bar = ""

    target_pos = (position * 100) / total

    for i in range(1, length + 1):
        i_pos = round(i * 100 / length)
        if i_pos <= target_pos:
            bar += filler
        else:
            bar += emptiness

    return bar if not in_brackets else f"[{bar}]"
