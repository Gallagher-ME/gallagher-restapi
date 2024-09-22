"""Test Gallagher Inputs methods."""

import pytest

from gallagher_restapi.client import Client


@pytest.mark.asyncio
async def test_get_operator_groups(gll_client: Client) -> None:
    """Test getting an input item."""
    operator_groups = await gll_client.get_operator_group(name="Admin")
    assert len(operator_groups) == 2


@pytest.mark.asyncio
async def test_get_operator_group_memebers(gll_client: Client) -> None:
    """Test getting an input item."""
    operator_groups = await gll_client.get_operator_group(name="Admin")
    assert operator_groups[0].cardholders
    operators = await gll_client.get_operator_group_members(
        href=operator_groups[0].cardholders.href
    )
    assert len(operators) > 0
    assert operators[0].name == "opc"
