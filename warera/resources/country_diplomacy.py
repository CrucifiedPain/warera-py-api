from __future__ import annotations
from ..models.country_diplomacy import CountryDiplomacy
from ._base import BaseResource

class CountryDiplomacyResource(BaseResource):
    """
    Endpoints:
      • countryDiplomacy.getByCountry
    """
    async def get_by_country(self, country_id: str) -> CountryDiplomacy:
        raw = await self._get("countryDiplomacy.getByCountry", countryId=country_id)
        return CountryDiplomacy.model_validate(raw)
