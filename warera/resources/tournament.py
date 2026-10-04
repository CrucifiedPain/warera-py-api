from __future__ import annotations

from typing import Any

from ..models.common import CursorPage
from ..models.tournament import Tournament, TournamentTeam
from ._base import BaseResource


class TournamentResource(BaseResource):
    """
    Endpoints:
      • tournament.getById
      • tournament.getLastTournament
      • tournament.getManyPaginated
      • tournamentTeam.getById
      • tournamentTeam.getByTournamentId
    """

    async def get(self, tournament_id: str) -> Tournament:
        """Get a tournament by its unique ID."""
        raw = await self._get("tournament.getById", tournamentId=tournament_id)
        return Tournament.model_validate(raw)

    async def get_last_tournament(self) -> Tournament:
        """Get the latest tournament details."""
        raw = await self._get("tournament.getLastTournament")
        return Tournament.model_validate(raw)

    async def get_many_paginated(
        self, *, limit: int | None = None, cursor: str | None = None
    ) -> CursorPage[Tournament]:
        """Get tournaments with cursor pagination."""
        kwargs: dict[str, Any] = {}
        if limit is not None:
            kwargs["limit"] = limit
        if cursor is not None:
            kwargs["cursor"] = cursor
        raw = await self._get("tournament.getManyPaginated", **kwargs)
        return CursorPage.from_raw(raw, Tournament)

    async def get_team_by_id(self, tournament_team_id: str) -> TournamentTeam:
        """Get a tournament team by its ID."""
        raw = await self._get(
            "tournamentTeam.getById",
            tournamentTeamId=tournament_team_id,
        )
        return TournamentTeam.model_validate(raw)

    async def get_teams_by_tournament(self, tournament_id: str) -> list[TournamentTeam]:
        """Get all teams for a specific tournament."""
        raw = await self._get(
            "tournamentTeam.getByTournamentId",
            tournamentId=tournament_id,
        )
        if isinstance(raw, list):
            return [TournamentTeam.model_validate(item) for item in raw]
        return []

    async def get_by_id(self, tournament_id: str) -> Tournament:
        """Get tournament by ID."""
        return await self.get(tournament_id)
