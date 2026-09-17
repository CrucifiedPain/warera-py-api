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
        self, country_id: str
    ) -> list[UnrestContribution]:
        """Get the unrest contributions for a country."""
        raw = await self._get(
            "contribution.getCountryUnrestContributions", countryId=country_id
        )
        return [UnrestContribution.model_validate(r) for r in raw]

    async def get_region_contributions(self, region_id: str) -> list[UnrestContribution]:
        """Get the unrest contributions for a region."""
        raw = await self._get(
            "contribution.getRegionContributions", regionId=region_id
        )
        return [UnrestContribution.model_validate(r) for r in raw]
