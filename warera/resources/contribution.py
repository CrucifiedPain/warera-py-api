from __future__ import annotations

from ..models.contribution import UnrestContribution
from ._base import BaseResource


class ContributionResource(BaseResource):
    """
    Endpoints:
      • contribution.getCountryUnrestContributions
      • contribution.getRegionContributions
    """

    async def get_country_unrest_contributions(
        self,
        country_id: str,
        *,
        page: int | None = None,
        limit: int | None = None,
    ) -> list[UnrestContribution]:
        """Get the unrest contributions for a country."""
        raw = await self._get(
            "contribution.getCountryUnrestContributions",
            countryId=country_id,
            page=page,
            limit=limit,
        )
        return self._parse_contributions(raw)

    async def get_region_contributions(
        self,
        region_id: str,
        *,
        page: int | None = None,
        limit: int | None = None,
    ) -> list[UnrestContribution]:
        """Get the unrest contributions for a region."""
        raw = await self._get(
            "contribution.getRegionContributions",
            regionId=region_id,
            page=page,
            limit=limit,
        )
        return self._parse_contributions(raw)

    @staticmethod
    def _parse_contributions(raw: object) -> list[UnrestContribution]:
        if isinstance(raw, list):
            return [UnrestContribution.model_validate(r) for r in raw if isinstance(r, dict)]
        if isinstance(raw, dict):
            items = raw.get("items", raw.get("data", []))
            if isinstance(items, list):
                return [UnrestContribution.model_validate(r) for r in items if isinstance(r, dict)]
        return []
