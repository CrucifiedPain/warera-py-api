from __future__ import annotations

from .common import WareraModel


class UnrestContribution(WareraModel):
    user_id: str | None = None
    user: str | None = None
    contribution: float | None = None
    amount: float | None = None
