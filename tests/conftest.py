"""Gallagher client fixture."""

from typing import Any, AsyncGenerator
import httpx
import pytest_asyncio

from gallagher_restapi import Client

from . import CONFIG


@pytest_asyncio.fixture(name="gll_client")
async def gll_client() -> AsyncGenerator[Any, Client]:
    """Return instance of Gallagher client."""
    async with httpx.AsyncClient(verify=False) as httpx_client:
        client = Client(
            CONFIG["api_key"],
            cloud_gateway=CONFIG["cloud_gateway"],
            # host=CONFIG["host"],
            # port=CONFIG["port"],
            httpx_client=httpx_client,
        )
        await client.initialize()
        yield client
