"""Test Gallagher Inputs methods."""
import pytest

from gallagher_restapi.client import Client


@pytest.mark.asyncio
async def test_get_input(gll_client: Client) -> None:
    """Test getting an input item."""
    inputs = await gll_client.get_input()
    if inputs:
        input = await gll_client.get_input(
            id=inputs[0].id, extra_fields=["statusFlags"]
        )
        assert input[0].statusFlags == ["open"]


@pytest.mark.asyncio
async def test_override_input(gll_client: Client) -> None:
    """Test overriding an input item."""
    if inputs := await gll_client.get_input():
        input = await gll_client.get_input(id=inputs[0].id)
        assert input[0].name is not None
        assert input[0].commands
        await gll_client.override_fence_zone(input[0].commands.shunt)
        new_input = await gll_client.get_input(
            id=input[0].id, extra_fields=["statusFlags"]
        )
        assert new_input[0].statusFlags == ["notPolled"]

        await gll_client.override_fence_zone(input[0].commands.unshunt)
        new_input = await gll_client.get_input(
            id=input[0].id, extra_fields=["statusFlags"]
        )
        assert new_input[0].statusFlags == ["open"]
