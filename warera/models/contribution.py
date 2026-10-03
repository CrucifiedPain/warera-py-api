from __future__ import annotations

from pydantic import AliasChoices, Field

from .common import WareraModel


class UnrestContribution(WareraModel):
    citizen_id: str | None = Field(
        default=None, validation_alias=AliasChoices("citizenId", "citizen_id", "userId", "user_id")
    )
    user_id: str | None = Field(
        default=None, validation_alias=AliasChoices("userId", "user_id", "citizenId", "citizen_id")
    )
    user: str | None = None
    contribution: float | None = None
    amount: float | None = None
    value: float | None = None

