from __future__ import annotations

import typing
from collections.abc import AsyncIterator

from .._enums import MercenaryAuctionStatus
from ..models.common import CursorPage
from ..models.mercenary_contract_auction import MercenaryContractAuction
from ._base import BaseResource


class MercenaryContractAuctionResource(BaseResource):
    """
    Endpoints:
      • mercenaryContractAuction.getPaginatedAuctions
    """

    @typing.overload
    async def get_paginated_auctions(
        self,
        *,
        country_id: str | None = None,
        for_country: str | None = None,
        for_country_side: str | None = None,
        battle_id: str | None = None,
        status: MercenaryAuctionStatus | str | None = None,
        professionals_only: bool | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
        page: int | None = None,
        limit: int = 10,
        cursor: str | None = None,
        auto_items: typing.Literal[True],
        max_pages: int | float = float("inf"),
        cursor_end: str | None = None,
    ) -> AsyncIterator[MercenaryContractAuction]: ...

    @typing.overload
    async def get_paginated_auctions(
        self,
        *,
        country_id: str | None = None,
        for_country: str | None = None,
        for_country_side: str | None = None,
        battle_id: str | None = None,
        status: MercenaryAuctionStatus | str | None = None,
        professionals_only: bool | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
        page: int | None = None,
        limit: int = 10,
        cursor: str | None = None,
        auto_items: typing.Literal[False] = False,
        max_pages: int | float = float("inf"),
        cursor_end: str | None = None,
    ) -> CursorPage[MercenaryContractAuction]: ...

    async def get_paginated_auctions(
        self,
        *,
        country_id: str | None = None,
        for_country: str | None = None,
        for_country_side: str | None = None,
        battle_id: str | None = None,
        status: MercenaryAuctionStatus | str | None = None,
        professionals_only: bool | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
        page: int | None = None,
        limit: int = 10,
        cursor: str | None = None,
        auto_items: bool = False,
        max_pages: int | float = float("inf"),
        cursor_end: str | None = None,
    ) -> CursorPage[MercenaryContractAuction] | AsyncIterator[MercenaryContractAuction]:
        """
        Get mercenary contract auctions (paginated).

        Args:
            country_id:         Alias for for_country (backward compatibility).
            for_country:        Country ID the auction is for.
            for_country_side:   Side ('attacker' or 'defender').
            battle_id:          Battle ID to filter auctions.
            status:             Auction status (e.g. 'active', 'completed').
            professionals_only: Filter by professional mercenaries only.
            sort_by:            Sort field.
            sort_order:         Sort direction ('asc' or 'desc').
            page:               Page number.
            limit:              Number of items per page.
            cursor:             Cursor for cursor-based pagination.
            auto_items:         Yield all items across pages when True.
            max_pages:          Max pages to fetch with auto_items.
            cursor_end:         Stop pagination at this cursor.
        """
        target_country = for_country or country_id
        if auto_items:
            from .._pagination import auto_paginate_items

            return auto_paginate_items(
                self.get_paginated_auctions,
                max_pages=max_pages,
                cursor=cursor,
                cursor_end=cursor_end,
                for_country=target_country,
                for_country_side=for_country_side,
                battle_id=battle_id,
                status=status,
                professionals_only=professionals_only,
                sort_by=sort_by,
                sort_order=sort_order,
                page=page,
                limit=limit,
            )

        raw = await self._get(
            "mercenaryContractAuction.getPaginatedAuctions",
            forCountry=target_country,
            forCountrySide=for_country_side,
            battleId=battle_id,
            status=status,
            professionalsOnly=professionals_only,
            sortBy=sort_by,
            sortOrder=sort_order,
            page=page,
            limit=limit,
            cursor=cursor,
        )
        return CursorPage.from_raw(raw, MercenaryContractAuction)

    async def collect_all(self, **kwargs: typing.Any) -> list[MercenaryContractAuction]:
        """Fetch all items across all pages concurrently using parallel time-slicing."""
        import warnings

        warnings.warn(
            "`collect_all()` is deprecated. Use `get_paginated(auto_items=True)` directly.",
            DeprecationWarning,
            stacklevel=2,
        )
        from .._pagination import parallel_collect_all

        fetch_fn = (
            getattr(self, "get_paginated", None)
            or getattr(self, "get_many", None)
            or getattr(self, "get_all", None)
        )
        if fetch_fn is None:
            raise NotImplementedError("Pagination not supported on this resource")

        return await parallel_collect_all(
            fetch_fn,
            oldest_date=kwargs.pop("oldest_date", None),
            time_slice_days=kwargs.pop("time_slice_days", 0.2),
            concurrency=kwargs.pop("concurrency", 500),
            **kwargs,
        )
