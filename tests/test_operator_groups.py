"""Test Gallagher Operator methods."""

from gallagher_restapi import Client


async def test_get_operator_groups(gll_client: Client) -> None:
    """Test getting an input item."""
    operator_groups = await gll_client.get_operator_group(name="Admin")
    assert len(operator_groups) == 2


async def test_get_operator_group_memebers(gll_client: Client) -> None:
    """Test getting an input item."""
    operator_groups = await gll_client.get_operator_group(
        name="Admin", response_fields=["cardholders"]
    )
    assert operator_groups[0].cardholders
    operators = await gll_client.get_operator_group_members(
        href=operator_groups[0].cardholders.href, response_fields=["cardholder", "href"]
    )
    assert len(operators) > 0
