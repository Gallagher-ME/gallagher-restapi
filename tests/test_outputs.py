"""Test Gallagher Outputs methods."""
import pytest

from gallagher_restapi.client import Client


@pytest.mark.asyncio
async def test_get_output(gll_client: Client) -> None:
    """Test getting an output item."""
    outputs = await gll_client.get_output(name="Test")
    if outputs:
        output = await gll_client.get_output(
            id=outputs[0].id, extra_fields=["defaults", "statusFlags"]
        )
        assert output[0].statusFlags == ["open"]


@pytest.mark.asyncio
async def test_override_output(gll_client: Client) -> None:
    """Test overriding an output item."""
    if outputs := await gll_client.get_output(name="Test"):
        output = await gll_client.get_output(id=outputs[0].id)
        assert output[0].name is not None
        assert output[0].commands
        await gll_client.override_fence_zone(output[0].commands.on)
        new_input = await gll_client.get_output(
            id=output[0].id, extra_fields=["defaults", "statusFlags"]
        )
        assert new_input[0].statusFlags == ["closed", "overridden"]

        await gll_client.override_fence_zone(output[0].commands.cancel)
        new_input = await gll_client.get_output(
            id=output[0].id, extra_fields=["defaults", "statusFlags"]
        )
        assert new_input[0].statusFlags == ["open"]
