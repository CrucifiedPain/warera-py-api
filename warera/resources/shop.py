from __future__ import annotations
from ..models.shop import ShopGift, ShopSubscribedUser, ShopGiftGiver
from ._base import BaseResource

class ShopResource(BaseResource):
    """
    Endpoints:
      • shop.getLastGifts
      • shop.getSubscribedUsers
      • shop.getTopGiftGivers
    """
    async def get_last_gifts(self) -> list[ShopGift]:
        raw = await self._get("shop.getLastGifts")
        return [ShopGift.model_validate(r) for r in raw]

    async def get_subscribed_users(self) -> list[ShopSubscribedUser]:
        raw = await self._get("shop.getSubscribedUsers")
        return [ShopSubscribedUser.model_validate(r) for r in raw]

    async def get_top_gift_givers(self) -> list[ShopGiftGiver]:
        raw = await self._get("shop.getTopGiftGivers")
        return [ShopGiftGiver.model_validate(r) for r in raw]
