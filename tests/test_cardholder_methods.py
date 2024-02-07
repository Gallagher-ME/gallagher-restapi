"""Test cardholder methods."""
from unittest.mock import patch
import pytest

from gallagher_restapi.client import Client
from gallagher_restapi.models import FTCardholder, FTItemReference, SortMethod


@pytest.mark.asyncio
async def test_get_cardholder_by_id(gll_client: Client) -> None:
    """Test getting cardholder by id."""
    cardholder = await gll_client.get_cardholder(id="1366")
    assert len(cardholder) == 1


@pytest.mark.asyncio
async def test_get_cardholder_by_name(gll_client: Client) -> None:
    """Test getting cardholder by name."""
    cardholder = await gll_client.get_cardholder(name="Justin", top=1)
    assert len(cardholder) == 1


@pytest.mark.asyncio
async def test_get_cardholder_by_pdf_value(gll_client: Client) -> None:
    """Test getting cardholder by pdf value."""
    cardholder = await gll_client.get_cardholder(pdfs={"Email": "newemail@mail.com"})
    assert len(cardholder) == 1


@pytest.mark.asyncio
async def test_add_cardholder(gll_client: Client) -> None:
    """Test adding a cardholder."""
    with patch(
        "gallagher_restapi.Client._async_request",
        return_value={"location": "https://location"},
    ):
        cardholder = FTCardholder(
            division=FTItemReference(href="https://division-href"),
            firstName="John",
            lastName="Doe",
        )
        new_cardholder_href = await gll_client.add_cardholder(cardholder)

    assert new_cardholder_href.href == "https://location"
