"""Test cardholder methods."""
from unittest.mock import patch
import pytest

from gallagher_restapi.client import Client
from gallagher_restapi.models import FTCardholder, FTItemReference


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


@pytest.mark.asyncio
async def test_get_card_type(gll_client: Client) -> None:
    """Test getting card types."""
    card_types = await gll_client.get_card_type()
    assert len(card_types) >= 1
    card_type = await gll_client.get_card_type(
        id=card_types[0].id, extra_fields=["credentialClass"]
    )
    assert len(card_type) == 1


@pytest.mark.asyncio
async def test_get_personal_data_field(gll_client: Client) -> None:
    """Test getting personal data field."""
    pdf_definitions = await gll_client.get_personal_data_field()
    assert len(pdf_definitions) >= 1
    pdf_defenition = await gll_client.get_personal_data_field(id=pdf_definitions[0].id)
    assert len(pdf_defenition) == 1


@pytest.mark.asyncio
async def test_get_image_from_pdf(gll_client: Client) -> None:
    """Test getting image from personal data field."""
    cardholders = await gll_client.get_cardholder(id="1012")
    cardholder = cardholders[0]
    assert cardholder.personalDataDefinitions
    for pdf in cardholder.personalDataDefinitions:
        for pdf_info in pdf.values():
            assert pdf_info.definition
            if pdf_info.definition.type == "image":
                assert isinstance(pdf_info.value, FTItemReference)
                image = await gll_client.get_image_from_pdf(pdf_info.value)
                assert image is not None
