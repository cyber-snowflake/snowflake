#  Copyright (c) 2020 — present, moretzu (モーレツ)
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, ClassVar, TypedDict

from aiohttp import ClientSession

from tomodachi.core.exceptions import AniListException

__all__ = ["AniList", "AniMedia"]


class MediaTitle(TypedDict):
    romaji: Optional[str]
    english: Optional[str]
    native: Optional[str]


class MediaCoverImage:
    __slots__ = ("extra_large", "large", "medium", "color")

    def __init__(self, **kwargs):
        self.extra_large = kwargs.get("extraLarge")
        self.large = kwargs.get("large")
        self.medium = kwargs.get("medium")
        self.color = kwargs.get("color")


class AniMedia:
    __slots__ = (
        "id",
        "title",
        "type",
        "description",
        "genres",
        "duration",
        "_startDate",
        "mean_score",
        "status",
        "_coverImage",
        "banner_image",
        "url",
    )

    def __init__(self, **kwargs):
        self.id: int = kwargs.get("id")
        self.title: MediaTitle = kwargs.get("title", {})
        self.type: str = kwargs.get("type")
        self.description: str = kwargs.get("description")
        self.genres: list[str] = kwargs.get("genres", [])
        self.duration: int = kwargs.get("duration", 0)
        self._startDate: dict[str, int] = kwargs.get("startDate", {})
        self.mean_score: int = kwargs.get("meanScore")
        self.status: str = kwargs.get("status")
        self._coverImage: dict[str, str] = kwargs.get("coverImage")
        self.banner_image: str = kwargs.get("bannerImage")
        self.url: str = kwargs.get("siteUrl")

    def __repr__(self):
        return f"<AniMedia id={self.id} title={self.title}>"

    @property
    def start_date(self):
        return datetime(self._startDate["year"], self._startDate["month"], self._startDate["day"], tzinfo=timezone.utc)

    @property
    def cover_image(self):
        return MediaCoverImage(**self._coverImage)


class AniList:
    __base_url: ClassVar[str] = "https://graphql.anilist.co"
    __session: ClassVar[Optional[ClientSession]] = None

    @classmethod
    async def setup(cls, session):
        cls.__session = session

    @classmethod
    async def lookup(cls, search: str, *, raw=False):
        query = """
                query ($id: Int, $page: Int, $search: String) {
                  Page(page: $page, perPage: 100) {
                    pageInfo {
                      total
                      currentPage
                      lastPage
                      hasNextPage
                      perPage
                    }
                    media(id: $id, search: $search, type: ANIME, sort: POPULARITY_DESC) {
                      type
                      id
                      title {
                        romaji
                        english
                        native
                      }
                      description
                      genres
                      duration
                      startDate {
                        year
                        month
                        day
                      }
                      meanScore
                      status
                      coverImage {
                        extraLarge
                        large
                        medium
                        color
                      }
                      bannerImage
                      siteUrl
                    }
                  }
                }
        """

        variables = {
            "search": search,
            "page": 1,
        }

        response = await cls.__session.post(cls.__base_url, json={"query": query, "variables": variables})
        _json = await response.json()

        if "errors" in _json.keys():
            raise AniListException(_json)

        if raw:
            return _json
        else:
            return [AniMedia(**obj) for obj in _json["data"]["Page"]["media"]]
