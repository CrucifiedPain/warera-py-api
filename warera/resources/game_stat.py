from __future__ import annotations

from typing import Any

from ._base import BaseResource


class GameStatResource(BaseResource):
    """
    Endpoints:
      • gameStat.getWorldDevelopment
      • gameStat.getEquipmentAvgByCode
    """

    async def get_world_development(self) -> dict[str, Any]:
        """Get the world development statistics."""
        return await self._get("gameStat.getWorldDevelopment")

    async def get_equipment_avg(self, item_code: str) -> float:
        """
        Get the average quality/stat value for a given equipment item code.

        Args:
            item_code: The item code to look up (e.g. ``"helmet"``, ``"sword"``).

        Returns:
            A float representing the average equipment value.
        """
        raw = await self._get("gameStat.getEquipmentAvgByCode", itemCode=item_code)
        if isinstance(raw, (int, float)):
            return float(raw)
        if isinstance(raw, dict):
            # Handle potential wrapped response
            for key in ("value", "avg", "average", "result"):
                val = raw.get(key)
                if val is not None:
                    return float(val)
        return float(raw)
