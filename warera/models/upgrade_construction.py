from __future__ import annotations

from pydantic import AliasChoices, Field

from .common import WareraModel


class UpgradeConstruction(WareraModel):
    """
    An in-progress region upgrade construction project.

    Used by the ``upgradeConstruction`` endpoints:
      • upgradeConstruction.getMapConstructions
      • upgradeConstruction.getRegionConstructions
      • upgradeConstruction.listConstructions
    """

    region_id: str | None = Field(
        default=None, validation_alias=AliasChoices("region", "regionId", "region_id")
    )
    country_id: str | None = Field(
        default=None, validation_alias=AliasChoices("country", "countryId", "country_id")
    )
    upgrade_type: str | None = Field(
        default=None, validation_alias=AliasChoices("upgradeType", "upgrade_type", "type")
    )
    level: int | None = None
    status: str | None = None
    invested_money: float | None = None
    invested_concrete: float | None = None
    invested_steel: float | None = None
    progress: float | None = None
    total_needed_money: float | None = None
    total_needed_concrete: float | None = None
    total_needed_steel: float | None = None
    start_time: str | None = None
    end_time: str | None = None
    will_be_active_at: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
