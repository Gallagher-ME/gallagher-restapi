"""Test Gallagher Outputs methods."""

import asyncio
from datetime import timedelta
from typing import TYPE_CHECKING

from gallagher_restapi import Client


async def test_get_output(gll_client: Client) -> None:
    """Test getting an output item."""
    outputs = await gll_client.get_output(name="7000")
    if outputs:
        output = await gll_client.get_output(
            id=outputs[0].id, response_fields=["statusFlags"]
        )
        assert output[0].status_flags == ["controllerOffline"]


async def test_override_output(gll_client: Client) -> None:
    """Test overriding an output item."""
    if outputs := await gll_client.get_output(name="Class"):
        output = await gll_client.get_output(id=outputs[0].id)
        assert output[0].name is not None
        if TYPE_CHECKING:
            assert output[0].commands
            assert output[0].commands.on
            assert output[0].commands.cancel
        await gll_client.override_output(
            output[0].commands.on, end_time=timedelta(seconds=5)
        )
        new_output = await gll_client.get_output(
            id=output[0].id, response_fields=["statusFlags"]
        )
        assert new_output[0].status_flags == ["closed", "overridden"]

        await gll_client.override_output(output[0].commands.cancel)
        await asyncio.sleep(1)
        new_output = await gll_client.get_output(
            id=output[0].id, response_fields=["statusFlags"]
        )
        assert new_output[0].status_flags == ["open"]
