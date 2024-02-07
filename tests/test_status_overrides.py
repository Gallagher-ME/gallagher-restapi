"""Test getting the status of items."""
import pytest

from gallagher_restapi.client import Client


@pytest.mark.asyncio
async def test_plugins_list(gll_client: Client) -> None:
    """Test the plugins list response."""
    controllers = await gll_client.get_item(item_type="Controller 6000")
    controller_status, update = await gll_client.get_item_status(
        [controller.id for controller in controllers]
    )
    assert controller_status is not None

    controller_new_status = await gll_client.get_item_status(next_link=update)
    assert controller_new_status is not None
