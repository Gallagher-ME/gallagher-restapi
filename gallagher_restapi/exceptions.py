"""The exceptions raised by the api."""


class GllApiError(Exception):
    """General GllApi exception."""


class ConnectError(GllApiError):
    """Error connecting to Gallagher server."""


class Unauthorized(GllApiError):
    """Authentication failed."""


class LicenseError(GllApiError):
    """Missing license error."""


class RequestError(GllApiError):
    """Request error."""
