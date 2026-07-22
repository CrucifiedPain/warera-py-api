import asyncio

import pytest

from warera._swr import SWRCache


@pytest.mark.asyncio
async def test_swr_cache_basic_fetch():
    cache = SWRCache()
    fetches = 0

    async def fetcher():
        nonlocal fetches
        fetches += 1
        await asyncio.sleep(0.01)
        return "data"

    # First fetch should block and return data
    res = await cache.get("key1", 10.0, fetcher)
    assert res == "data"
    assert fetches == 1

    # Second fetch should return immediately from cache
    res2 = await cache.get("key1", 10.0, fetcher)
    assert res2 == "data"
    assert fetches == 1


@pytest.mark.asyncio
async def test_swr_cache_stale_revalidate():
    cache = SWRCache()
    fetches = 0

    async def fetcher():
        nonlocal fetches
        fetches += 1
        await asyncio.sleep(0.05)
        return f"data_{fetches}"

    # Initial fetch
    res1 = await cache.get("key", 0.01, fetcher)
    assert res1 == "data_1"
    assert fetches == 1

    # Wait for TTL to expire
    await asyncio.sleep(0.02)

    # Next fetch should instantly return stale data, but trigger revalidate
    res2 = await cache.get("key", 0.01, fetcher)
    assert res2 == "data_1"  # Returns stale data instantly

    # Allow the background revalidation task to finish
    await asyncio.sleep(0.1)

    assert fetches == 2

    # Next fetch should return the newly revalidated data
    res3 = await cache.get("key", 0.01, fetcher)
    assert res3 == "data_2"


@pytest.mark.asyncio
async def test_swr_cache_concurrent_fetches():
    cache = SWRCache()
    fetches = 0

    async def fetcher():
        nonlocal fetches
        fetches += 1
        await asyncio.sleep(0.1)
        return "data"

    # Fire 5 concurrent requests for the same key
    results = await asyncio.gather(*(cache.get("key", 10.0, fetcher) for _ in range(5)))

    # All should get the data, but fetcher should only be called ONCE
    for r in results:
        assert r == "data"
    assert fetches == 1

@pytest.mark.asyncio
async def test_swr_cache_eviction():
    cache = SWRCache()
    
    async def fetcher():
        return "data"
        
    for i in range(1005):
        await cache.get(f"key_{i}", 10.0, fetcher)
        
    assert cache._cache.get_size() == 1000
    assert cache._cache.get("key_0") is None
    assert cache._cache.get("key_1004") is not None


@pytest.mark.asyncio
async def test_swr_revalidate_creates_single_task():
    """A stale revalidation must create exactly one inflight task, not two."""
    cache = SWRCache()

    async def fetcher():
        await asyncio.sleep(0.05)
        return "v"

    # Prime the cache with a stale entry.
    await cache.get("k", 0.01, fetcher)
    await asyncio.sleep(0.02)

    # Trigger background revalidation; exactly one inflight task should exist.
    await cache.get("k", 0.01, fetcher)
    assert len(cache._inflight) == 1
    inflight_task = next(iter(cache._inflight.values()))

    await asyncio.sleep(0.1)
    assert inflight_task.done()
    assert len(cache._inflight) == 0


@pytest.mark.asyncio
async def test_swr_blocking_backend_store_is_tracked_and_persists(tmp_path):
    """
    With a blocking backend, the fire-and-forget store task must be strongly
    referenced (so the loop can't GC it mid-write) and the value must persist.
    """
    from warera.cache_backends import SQLiteCacheBackend

    db = str(tmp_path / "swr.sqlite")
    cache = SWRCache(backend=SQLiteCacheBackend(db))

    async def fetcher():
        return {"v": 1}

    result = await cache.get("k", 10.0, fetcher)
    assert result == {"v": 1}

    # Allow the background store task to complete.
    await asyncio.sleep(0.2)

    # The write must have persisted to disk (would be lost if the task was GC'd).
    persisted = SQLiteCacheBackend(db).get("k")
    assert persisted is not None
    assert persisted[0] == {"v": 1}
    # Completed store tasks are discarded from the tracking set.
    assert len(cache._store_tasks) == 0
