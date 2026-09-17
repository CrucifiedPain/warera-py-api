from __future__ import annotations
from typing import Any
from ..models.common import CursorPage
from ..models.sanction import Sanction
from ._base import BaseResource

class SanctionResource(BaseResource):
    """
    Endpoints:
      • sanction.getPaginated
    """
    async def get_paginated(
        self, target_user_id: str | None = None, type_: str | None = None, *, limit: int | None = None, cursor: str | None = None
    ) -> CursorPage[Sanction]:
        kwargs: dict[str, Any] = {}
        if target_user_id is not None:
            kwargs["targetUserId"] = target_user_id
        if type_ is not None:
            kwargs["type"] = type_
        if limit is not None:
            kwargs["limit"] = limit
        if cursor is not None:
            kwargs["cursor"] = cursor
        raw = await self._get("sanction.getPaginated", **kwargs)
        return CursorPage.from_raw(raw, Sanction)
