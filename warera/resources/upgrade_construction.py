from __future__ import annotations

import typing
from collections.abc import AsyncIterator

from ..models.common import CursorPage
from ..models.upgrade_construction import UpgradeConstruction
from ._base import BaseResource


class UpgradeConstructionResource(BaseResource):
    """
    Endpoints:
      • upgradeConstruction.getMapConstructions
      • upgradeConstruction.getRegionConstructions
      • upgradeConstruction.listConstructions
    """

    async def get_map_constructions(self) -> list[UpgradeConstruction]:
        """
        Retrieve every in-progress region-upgrade construction project across the whole map.

        No parameters required. Returns an empty list when nothing is currently under
        construction anywhere.
        """
        raw = await self._get("upgradeConstruction.getMapConstructions")
        if isinstance(raw, list):
            return [
                UpgradeConstruction.model_validate(item)
                for item in raw
                if isinstance(item, dict)
            ]
        if isinstance(raw, dict):
            items = raw.get("items", raw.get("data", []))
            if isinstance(items, list):
                return [
                    UpgradeConstruction.model_validate(item)
                    for item in items
                    if isinstance(item, dict)
                ]
        return []

    async def get_region_constructions(self, region_id: str) -> list[UpgradeConstruction]:
        """
        Retrieve every in-progress upgrade construction project for a specific region.

        Args:
            region_id: Unique identifier of the region.

        Returns an empty list when that region has nothing currently under construction.
        """
        raw = await self._get(
            "upgradeConstruction.getRegionConstructions",
            regionId=region_id,
        )
        if isinstance(raw, list):
            return [
                UpgradeConstruction.model_validate(item)
                for item in raw
                if isinstance(item, dict)
            ]
        if isinstance(raw, dict):
            items = raw.get("items", raw.get("data", []))
            if isinstance(items, list):
                return [
                    UpgradeConstruction.model_validate(item)
                    for item in items
                    if isinstance(item, dict)
                ]
        return []

    @typing.overload
    async def list_constructions(
        self,
        *,
        region_id: str | None = None,
        country_id: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
        auto_items: typing.Literal[True],
        max_pages: int | float = float("inf"),
        cursor_end: str | None = None,
    ) -> AsyncIterator[UpgradeConstruction]: ...

    @typing.overload
    async def list_constructions(
        self,
        *,
        region_id: str | None = None,
        country_id: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
        auto_items: typing.Literal[False] = False,
        max_pages: int | float = float("inf"),
        cursor_end: str | None = None,
    ) -> CursorPage[UpgradeConstruction]: ...

    async def list_constructions(
        self,
        *,
        region_id: str | None = None,
        country_id: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
        auto_items: bool = False,
        max_pages: int | float = float("inf"),
        cursor_end: str | None = None,
    ) -> CursorPage[UpgradeConstruction] | AsyncIterator[UpgradeConstruction]:
        """
        Retrieve a paginated list of upgrade construction projects filtered by region or country.

        At least one of region_id or country_id must be provided.
        Cursor pagination uses the construction document's own Mongo _id.

        Args:
            region_id:   Filter by region ID.
            country_id:  Filter by country ID.
            limit:       Maximum number of items per page.
            cursor:      Pagination cursor (the Mongo _id from the previous page).
            auto_items:  When True, yields items across all pages.
            max_pages:   Max number of pages to fetch when auto_items=True.
            cursor_end:  Optional cursor to stop pagination at.
        """
        if region_id is None and country_id is None:
            raise ValueError("At least one of region_id or country_id must be provided")

        if auto_items:
            from .._pagination import auto_paginate_items

            return auto_paginate_items(
                self.list_constructions,
                max_pages=max_pages,
                cursor=cursor,
                cursor_end=cursor_end,
                region_id=region_id,
                country_id=country_id,
                limit=limit,
            )

        raw = await self._get(
            "upgradeConstruction.listConstructions",
            regionId=region_id,
            countryId=country_id,
            limit=limit,
            cursor=cursor,
        )
        return CursorPage.from_raw(raw, UpgradeConstruction)
