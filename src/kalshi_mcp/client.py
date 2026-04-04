"""Async HTTP client for the Kalshi prediction market REST API."""

import time
from typing import Any

import httpx

from kalshi_mcp.auth import load_private_key, sign_request

DEFAULT_BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"


class KalshiClient:
    """Thin async wrapper around Kalshi's REST API.

    Signs authenticated requests automatically using RSA-PSS.
    """

    def __init__(
        self,
        api_key: str,
        private_key_path: str,
        base_url: str = DEFAULT_BASE_URL,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.private_key = load_private_key(private_key_path)
        self._http: httpx.AsyncClient | None = None

    async def _get_http(self) -> httpx.AsyncClient:
        if self._http is None or self._http.is_closed:
            self._http = httpx.AsyncClient(timeout=30.0)
        return self._http

    async def close(self) -> None:
        if self._http and not self._http.is_closed:
            await self._http.aclose()

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        auth_required: bool = True,
    ) -> dict[str, Any]:
        """Send a request to the Kalshi API.

        Args:
            method: HTTP method (GET, POST, DELETE, etc.).
            path: API path relative to base URL (e.g. /events).
            params: Optional query parameters.
            json_body: Optional JSON request body.
            auth_required: Whether to include auth headers.

        Returns:
            Parsed JSON response as a dict.
        """
        url = f"{self.base_url}{path}"
        headers: dict[str, str] = {"Content-Type": "application/json"}

        if auth_required:
            timestamp_ms = str(int(time.time() * 1000))
            # Sign with the full path including the base path portion
            # The path for signing is everything after the host
            full_path = f"/trade-api/v2{path}"
            auth_headers = sign_request(
                self.private_key,
                self.api_key,
                method.upper(),
                full_path,
                timestamp_ms,
            )
            headers.update(auth_headers)

        # Strip None values from params
        if params:
            params = {k: v for k, v in params.items() if v is not None}

        http = await self._get_http()
        response = await http.request(
            method=method.upper(),
            url=url,
            headers=headers,
            params=params,
            json=json_body,
        )
        response.raise_for_status()
        return response.json()

    # ── Exchange ──────────────────────────────────────────────

    async def get_exchange_status(self) -> dict[str, Any]:
        return await self._request("GET", "/exchange/status")

    async def get_exchange_schedule(self) -> dict[str, Any]:
        return await self._request("GET", "/exchange/schedule")

    # ── Events ────────────────────────────────────────────────

    async def get_events(
        self,
        *,
        limit: int | None = None,
        cursor: str | None = None,
        status: str | None = None,
        series_ticker: str | None = None,
        with_nested_markets: bool | None = None,
        min_close_ts: int | None = None,
    ) -> dict[str, Any]:
        return await self._request(
            "GET",
            "/events",
            params={
                "limit": limit,
                "cursor": cursor,
                "status": status,
                "series_ticker": series_ticker,
                "with_nested_markets": with_nested_markets,
                "min_close_ts": min_close_ts,
            },
        )

    async def get_event(
        self,
        event_ticker: str,
        *,
        with_nested_markets: bool | None = None,
    ) -> dict[str, Any]:
        return await self._request(
            "GET",
            f"/events/{event_ticker}",
            params={"with_nested_markets": with_nested_markets},
        )

    async def get_event_metadata(self, event_ticker: str) -> dict[str, Any]:
        return await self._request("GET", f"/events/{event_ticker}/metadata")

    # ── Markets ───────────────────────────────────────────────

    async def get_markets(
        self,
        *,
        limit: int | None = None,
        cursor: str | None = None,
        event_ticker: str | None = None,
        series_ticker: str | None = None,
        tickers: str | None = None,
        status: str | None = None,
    ) -> dict[str, Any]:
        return await self._request(
            "GET",
            "/markets",
            params={
                "limit": limit,
                "cursor": cursor,
                "event_ticker": event_ticker,
                "series_ticker": series_ticker,
                "tickers": tickers,
                "status": status,
            },
        )

    async def get_market(self, ticker: str) -> dict[str, Any]:
        return await self._request("GET", f"/markets/{ticker}")

    async def get_market_orderbook(
        self,
        ticker: str,
        *,
        depth: int | None = None,
    ) -> dict[str, Any]:
        return await self._request(
            "GET",
            f"/markets/{ticker}/orderbook",
            params={"depth": depth},
        )

    async def get_trades(
        self,
        *,
        ticker: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
        min_ts: int | None = None,
        max_ts: int | None = None,
    ) -> dict[str, Any]:
        return await self._request(
            "GET",
            "/markets/trades",
            params={
                "ticker": ticker,
                "limit": limit,
                "cursor": cursor,
                "min_ts": min_ts,
                "max_ts": max_ts,
            },
        )

    async def get_market_candlesticks(
        self,
        series_ticker: str,
        ticker: str,
        *,
        start_ts: int,
        end_ts: int,
        period_interval: int,
    ) -> dict[str, Any]:
        return await self._request(
            "GET",
            f"/series/{series_ticker}/markets/{ticker}/candlesticks",
            params={
                "start_ts": start_ts,
                "end_ts": end_ts,
                "period_interval": period_interval,
            },
        )

    # ── Series ────────────────────────────────────────────────

    async def get_series(self, series_ticker: str) -> dict[str, Any]:
        return await self._request("GET", f"/series/{series_ticker}")

    # ── Portfolio ─────────────────────────────────────────────

    async def get_balance(self) -> dict[str, Any]:
        return await self._request("GET", "/portfolio/balance")

    async def get_positions(
        self,
        *,
        limit: int | None = None,
        cursor: str | None = None,
        ticker: str | None = None,
        event_ticker: str | None = None,
        count_filter: str | None = None,
    ) -> dict[str, Any]:
        return await self._request(
            "GET",
            "/portfolio/positions",
            params={
                "limit": limit,
                "cursor": cursor,
                "ticker": ticker,
                "event_ticker": event_ticker,
                "count_filter": count_filter,
            },
        )

    async def get_orders(
        self,
        *,
        ticker: str | None = None,
        event_ticker: str | None = None,
        min_ts: int | None = None,
        max_ts: int | None = None,
        status: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        return await self._request(
            "GET",
            "/portfolio/orders",
            params={
                "ticker": ticker,
                "event_ticker": event_ticker,
                "min_ts": min_ts,
                "max_ts": max_ts,
                "status": status,
                "limit": limit,
                "cursor": cursor,
            },
        )

    async def create_order(
        self,
        *,
        ticker: str,
        side: str,
        action: str,
        count: int,
        order_type: str = "limit",
        yes_price: int | None = None,
        no_price: int | None = None,
        client_order_id: str | None = None,
        time_in_force: str | None = None,
        expiration_ts: int | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "ticker": ticker,
            "side": side,
            "action": action,
            "count": count,
            "type": order_type,
        }
        if yes_price is not None:
            body["yes_price"] = yes_price
        if no_price is not None:
            body["no_price"] = no_price
        if client_order_id is not None:
            body["client_order_id"] = client_order_id
        if time_in_force is not None:
            body["time_in_force"] = time_in_force
        if expiration_ts is not None:
            body["expiration_ts"] = expiration_ts
        return await self._request("POST", "/portfolio/orders", json_body=body)

    async def cancel_order(self, order_id: str) -> dict[str, Any]:
        return await self._request("DELETE", f"/portfolio/orders/{order_id}")

    async def get_fills(
        self,
        *,
        ticker: str | None = None,
        order_id: str | None = None,
        min_ts: int | None = None,
        max_ts: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        return await self._request(
            "GET",
            "/portfolio/fills",
            params={
                "ticker": ticker,
                "order_id": order_id,
                "min_ts": min_ts,
                "max_ts": max_ts,
                "limit": limit,
                "cursor": cursor,
            },
        )

    async def get_settlements(
        self,
        *,
        ticker: str | None = None,
        event_ticker: str | None = None,
        min_ts: int | None = None,
        max_ts: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        return await self._request(
            "GET",
            "/portfolio/settlements",
            params={
                "ticker": ticker,
                "event_ticker": event_ticker,
                "min_ts": min_ts,
                "max_ts": max_ts,
                "limit": limit,
                "cursor": cursor,
            },
        )
