"""Test Gallagher Outputs methods."""

from gallagher_restapi import Client


async def test_get_locker_bank(gll_client: Client) -> None:
    """Test getting a locker bank."""
    locker_banks = await gll_client.get_locker_bank(
        name="Locker Bank", response_fields=["lockers"]
    )
    if locker_banks:
        assert len(locker_banks) == 1
        assert locker_banks[0].lockers is not None


async def test_get_locker(gll_client: Client) -> None:
    """Test getting a locker item."""
    locker_banks = await gll_client.get_locker_bank(
        name="Locker Bank", response_fields=["lockers"]
    )
    assert locker_banks[0].lockers is not None

    locker = await gll_client.get_locker(
        id=locker_banks[0].lockers[0].href.split("/")[-1]
    )
    assert locker is not None
    assert locker.name == locker_banks[0].lockers[0].name
