"""Test getting the status of items."""

from gallagher_restapi import Client


async def test_get_item_status(gll_client: Client) -> None:
    """Test getting the status of items from Gallagher."""
    controllers = await gll_client.get_item(
        item_types=["Controller 6000"], response_fields=["statusFlags"]
    )
    controller_status, update = await gll_client.get_item_status(
        [controller.id for controller in controllers]
    )
    assert controller_status is not None

    controller_new_status = await gll_client.get_item_status(next_link=update)
    assert controller_new_status is not None
