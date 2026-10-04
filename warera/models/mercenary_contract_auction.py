from __future__ import annotations

from pydantic import Field

from .common import WareraModel


class MercenaryContractAuctionBid(WareraModel):
    bid_at: str | None = None
    mu: str | None = None
    payout: int | float | None = None
    per_k: int | float | None = None
    user: str | None = None


class MercenaryContractAuction(WareraModel):
    v: int | None = Field(default=None, alias="__v")
    battle: str | None = None
    bids: list[MercenaryContractAuctionBid] = Field(default_factory=list)
    budget: int | float | None = None
    country: str | None = None
    created_at: str | None = None
    created_by: str | None = None
    current_payout: int | float | None = None
    current_per_k: int | float | None = None
    current_winner: str | None = None
    current_winner_user: str | None = None
    duration: int | None = None
    expires_at: str | None = None
    for_country: str | None = None
    for_country_side: str | None = None
    initial_per_k: int | float | None = None
    minimum_damage: int | float | None = None
    professionals_only: bool | None = None
    round: str | None = None
    round_number: int | None = None
    status: str | None = None
    updated_at: str | None = None
