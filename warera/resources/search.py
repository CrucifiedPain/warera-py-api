from __future__ import annotations

from ..models.search import SearchResult, SearchResults
from ._base import BaseResource


class SearchResource(BaseResource):
    """
    Endpoints:
      • search.searchAnything
      • search.searchMus
      • search.searchUsers
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
        """
        Search military units by name.

        Args:
            query: The search text query.

        Returns:
            A list of SearchResult items representing matching military units.
        """
        raw = await self._get("search.searchMus", searchText=query)
        if isinstance(raw, list):
            return [
                SearchResult.model_validate({"id": r, "type": "mu"})
                if isinstance(r, str)
                else SearchResult.model_validate(r)
                for r in raw
            ]
        return []

    async def search_users(self, query: str) -> list[SearchResult]:
        """
        Search users by name or username.

        Args:
            query: The search text query.

        Returns:
            A list of SearchResult items representing matching users.
        """
        raw = await self._get("search.searchUsers", searchText=query)
        if isinstance(raw, list):
            return [
                SearchResult.model_validate({"id": r, "type": "user"})
                if isinstance(r, str)
                else SearchResult.model_validate(r)
                for r in raw
            ]
        return []
