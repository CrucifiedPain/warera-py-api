from __future__ import annotations

from ..models.search import SearchResult, SearchResults
from ._base import BaseResource


class SearchResource(BaseResource):
    """
    Endpoints:
      • search.searchAnything
    """

    async def query(self, search_text: str) -> SearchResults:
        """
        Global search across all entity types (users, countries, companies, MUs, articles).

        Args:
            search_text: The search query. Must be at least 1 character.

        Returns:
            SearchResults containing a list of matched entities with type and ID.
        """
        if not search_text.strip():
            raise ValueError("search_text must not be empty")

        raw = await self._get("search.searchAnything", searchText=search_text)

        results: list[SearchResult] = []
        if isinstance(raw, dict):
            # API returns {userIds: [...], muIds: [...], ...}
            mappings = {
                "userIds": "user",
                "muIds": "mu",
                "countryIds": "country",
                "regionIds": "region",
                "partyIds": "party",
                "articleIds": "article",
                "companyIds": "company",
            }
            for key, entity_type in mappings.items():
                ids = raw.get(key, [])
                if isinstance(ids, list):
                    for eid in ids:
                        results.append(
                            SearchResult.model_validate({"id": eid, "type": entity_type})
                        )

        return SearchResults(results=results, total=len(results))


    async def search_mus(self, query: str) -> list[SearchResult]:
        """Search military units by name. Returns a list of MU matches."""
        if not query.strip():
            raise ValueError("query must not be empty")
        raw = await self._get("search.searchMus", searchText=query)
        return self._results_from_ids(raw, "mu")

    async def search_users(self, query: str) -> list[SearchResult]:
        """Search users by name or username. Returns a list of user matches."""
        if not query.strip():
            raise ValueError("query must not be empty")
        raw = await self._get("search.searchUsers", searchText=query)
        return self._results_from_ids(raw, "user")

    @staticmethod
    def _results_from_ids(raw: object, entity_type: str) -> list[SearchResult]:
        """Build SearchResult objects from a raw list of ID strings."""
        if not isinstance(raw, list):
            return []
        return [
            SearchResult.model_validate({"id": eid, "type": entity_type})
            for eid in raw
            if isinstance(eid, str)
        ]
