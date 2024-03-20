"""Test getting the status of items."""
import httpx
import pytest

from gallagher_restapi import Client, UnauthorizedError, LicenseError

from . import CONFIG


@pytest.mark.asyncio
async def test_conn_successfull() -> None:
    """Test successfull connection to server."""

    async with httpx.AsyncClient(verify=False) as httpx_client:
        gll_client = Client(
            host=CONFIG["host"],
            port=CONFIG["port"],
            api_key=CONFIG["api_key"],
            httpx_client=httpx_client,
        )
        await gll_client.initialize()

    assert gll_client._item_types
    assert gll_client.event_types


@pytest.mark.asyncio
async def test_wrong_api_key() -> None:
    """Test using wrong api key."""

    config = CONFIG.copy()
    config["api_key"] = "wrong-key"

    async with httpx.AsyncClient(verify=False) as httpx_client:
        with pytest.raises(UnauthorizedError):
            gll_client = Client(
                host=config["host"],
                port=config["port"],
                api_key=config["api_key"],
                httpx_client=httpx_client,
            )
            await gll_client.initialize()


@pytest.mark.asyncio
async def test_feature_not_licensed(gll_client: Client) -> None:
    """Test requsting a feature that is not licensed."""
    gll_client.api_features.doors = None
    with pytest.raises(LicenseError):
        await gll_client.get_door(name="Test")
