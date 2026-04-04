"""RSA-SHA256 PSS request signing for Kalshi API authentication."""

import base64

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey


def load_private_key(path: str) -> RSAPrivateKey:
    """Load an RSA private key from a PEM file."""
    with open(path, "rb") as f:
        key = serialization.load_pem_private_key(f.read(), password=None)
    if not isinstance(key, RSAPrivateKey):
        raise TypeError(f"Expected RSA private key, got {type(key).__name__}")
    return key


def sign_request(
    private_key: RSAPrivateKey,
    api_key: str,
    method: str,
    path: str,
    timestamp_ms: str,
) -> dict[str, str]:
    """Sign a request and return the required Kalshi auth headers.

    Args:
        private_key: RSA private key for signing.
        api_key: Kalshi API key identifier.
        method: HTTP method (GET, POST, DELETE, etc.) — uppercase.
        path: Request path without query params (e.g. /trade-api/v2/markets).
        timestamp_ms: Unix timestamp in milliseconds as a string.

    Returns:
        Dict with KALSHI-ACCESS-KEY, KALSHI-ACCESS-TIMESTAMP,
        and KALSHI-ACCESS-SIGNATURE headers.
    """
    message = f"{timestamp_ms}{method}{path}".encode("utf-8")
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.DIGEST_LENGTH,
        ),
        hashes.SHA256(),
    )
    encoded_signature = base64.b64encode(signature).decode("utf-8")
    return {
        "KALSHI-ACCESS-KEY": api_key,
        "KALSHI-ACCESS-TIMESTAMP": timestamp_ms,
        "KALSHI-ACCESS-SIGNATURE": encoded_signature,
    }
