from __future__ import annotations
from typing import Any
from ..models.common import CursorPage
from ..models.giveaway import Giveaway
from ._base import BaseResource

class GiveawayResource(BaseResource):
    """
    Endpoints:
      • giveaway.getManyPaginated
    """
    async def get_many_paginated(
        self, *, limit: int | None = None, cursor: str | None = None
    ) -> CursorPage[Giveaway]:
        kwargs: dict[str, Any] = {}
        if limit is not None:
            kwargs["limit"] = limit
        if cursor is not None:
            kwargs["cursor"] = cursor
        raw = await self._get("giveaway.getManyPaginated", **kwargs)
        return CursorPage.from_raw(raw, Giveaway)
