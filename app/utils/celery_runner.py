import asyncio
from app.core.db.session import get_async_session


def run_async_with_db(async_fn, *args, **kwargs):

    async def run_with_session():
        async with get_async_session() as db:
            return await async_fn(db, *args, **kwargs)

    return asyncio.run(run_with_session())