from __future__ import annotations
from .common import WareraModel

class Sanction(WareraModel):
    target_user_id: str | None = None
    type: str | None = None
