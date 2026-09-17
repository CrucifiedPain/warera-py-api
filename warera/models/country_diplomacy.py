from __future__ import annotations
from .common import WareraModel

class CountryDiplomacy(WareraModel):
    country_id: str | None = None
    allies: list[str] | None = None
    enemies: list[str] | None = None
