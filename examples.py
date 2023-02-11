"""Examples for REST api client usage."""
import httpx


# TODO add example for using certificate
context = httpx.create_ssl_context(
    cert=(
        "/workspaces/codespaces-blank/cert.pem",
        "/workspaces/codespaces-blank/key.pem",
        "12345",
    ),
    verify=False,
)
