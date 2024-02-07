"""Gallagher client fixture."""
import httpx
import pytest_asyncio

from gallagher_restapi import Client

from . import CONFIG


@pytest_asyncio.fixture(name="gll_client")
async def gll_client() -> Client:
    """Return instance of Gallagher client."""
    async with httpx.AsyncClient(verify=False) as httpx_client:
        client = Client(
            CONFIG["api_key"],
            host=CONFIG["host"],
            port=CONFIG["port"],
            httpx_client=httpx_client,
        )
        await client.initialize()
        yield client
