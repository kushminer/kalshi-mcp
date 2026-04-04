"""MCP server exposing Kalshi prediction market API as tools."""

import json
import os

from mcp.server.fastmcp import FastMCP

from kalshi_mcp.client import KalshiClient

mcp = FastMCP("kalshi")

# Lazily initialized client (created on first tool call).
_client: KalshiClient | None = None


def _get_client() -> KalshiClient:
    global _client
    if _client is None:
        api_key = os.environ.get("KALSHI_API_KEY", "")
        private_key_path = os.environ.get("KALSHI_PRIVATE_KEY_PATH", "")
        base_url = os.environ.get(
            "KALSHI_API_BASE_URL",
            "https://api.elections.kalshi.com/trade-api/v2",
        )
        if not api_key or not private_key_path:
            raise RuntimeError(
                "KALSHI_API_KEY and KALSHI_PRIVATE_KEY_PATH environment "
                "variables are required"
            )
        _client = KalshiClient(api_key, private_key_path, base_url)
    return _client


def _json(data: dict) -> str:
    """Format a dict as indented JSON for readable tool output."""
    return json.dumps(data, indent=2)


# ── Exchange ──────────────────────────────────────────────────


@mcp.tool()
async def get_exchange_status() -> str:
    """Get the current exchange trading status."""
    result = await _get_client().get_exchange_status()
    return _json(result)


@mcp.tool()
async def get_exchange_schedule() -> str:
    """Get the exchange schedule."""
    result = await _get_client().get_exchange_schedule()
    return _json(result)


# ── Events ────────────────────────────────────────────────────


@mcp.tool()
async def get_events(
    limit: int | None = None,
    cursor: str | None = None,
    status: str | None = None,
    series_ticker: str | None = None,
    with_nested_markets: bool | None = None,
    min_close_ts: int | None = None,
) -> str:
    """List events with optional filters.

    Args:
        limit: Results per page (max 200).
        cursor: Pagination cursor from a previous response.
        status: Filter by status: unopened, open, closed, settled.
        series_ticker: Filter by series ticker.
        with_nested_markets: Include nested market objects in response.
        min_close_ts: Filter events closing after this Unix timestamp.
    """
    result = await _get_client().get_events(
        limit=limit,
        cursor=cursor,
        status=status,
        series_ticker=series_ticker,
        with_nested_markets=with_nested_markets,
        min_close_ts=min_close_ts,
    )
    return _json(result)


@mcp.tool()
async def get_event(
    event_ticker: str,
    with_nested_markets: bool | None = None,
) -> str:
    """Get a single event by ticker, optionally with its markets.

    Args:
        event_ticker: The event ticker identifier.
        with_nested_markets: Include nested market objects in response.
    """
    result = await _get_client().get_event(
        event_ticker, with_nested_markets=with_nested_markets
    )
    return _json(result)


# ── Markets ───────────────────────────────────────────────────


@mcp.tool()
async def get_markets(
    limit: int | None = None,
    cursor: str | None = None,
    event_ticker: str | None = None,
    series_ticker: str | None = None,
    tickers: str | None = None,
    status: str | None = None,
) -> str:
    """List markets with optional filters.

    Args:
        limit: Results per page (max 1000).
        cursor: Pagination cursor from a previous response.
        event_ticker: Filter by event ticker.
        series_ticker: Filter by series ticker.
        tickers: Comma-separated list of market tickers.
        status: Filter by status: unopened, open, paused, closed, settled.
    """
    result = await _get_client().get_markets(
        limit=limit,
        cursor=cursor,
        event_ticker=event_ticker,
        series_ticker=series_ticker,
        tickers=tickers,
        status=status,
    )
    return _json(result)


@mcp.tool()
async def get_market(ticker: str) -> str:
    """Get details for a single market by ticker.

    Args:
        ticker: The market ticker identifier.
    """
    result = await _get_client().get_market(ticker)
    return _json(result)


@mcp.tool()
async def get_market_orderbook(
    ticker: str,
    depth: int | None = None,
) -> str:
    """Get the orderbook for a market.

    Args:
        ticker: The market ticker.
        depth: Number of price levels to return (0 = all, 1-100).
    """
    result = await _get_client().get_market_orderbook(ticker, depth=depth)
    return _json(result)


@mcp.tool()
async def get_trades(
    ticker: str | None = None,
    limit: int | None = None,
    cursor: str | None = None,
    min_ts: int | None = None,
    max_ts: int | None = None,
) -> str:
    """Get recent trades, optionally filtered by market ticker.

    Args:
        ticker: Filter by market ticker.
        limit: Results per page (max 1000).
        cursor: Pagination cursor from a previous response.
        min_ts: Filter trades after this Unix timestamp.
        max_ts: Filter trades before this Unix timestamp.
    """
    result = await _get_client().get_trades(
        ticker=ticker,
        limit=limit,
        cursor=cursor,
        min_ts=min_ts,
        max_ts=max_ts,
    )
    return _json(result)


@mcp.tool()
async def get_market_candlesticks(
    series_ticker: str,
    ticker: str,
    start_ts: int,
    end_ts: int,
    period_interval: int,
) -> str:
    """Get OHLCV candlestick data for a market.

    Args:
        series_ticker: Series ticker containing the market.
        ticker: Market ticker.
        start_ts: Start Unix timestamp.
        end_ts: End Unix timestamp.
        period_interval: Candle period in minutes: 1 (minute), 60 (hour), or 1440 (day).
    """
    result = await _get_client().get_market_candlesticks(
        series_ticker,
        ticker,
        start_ts=start_ts,
        end_ts=end_ts,
        period_interval=period_interval,
    )
    return _json(result)


# ── Series ────────────────────────────────────────────────────


@mcp.tool()
async def get_series(series_ticker: str) -> str:
    """Get series metadata.

    Args:
        series_ticker: The series ticker identifier.
    """
    result = await _get_client().get_series(series_ticker)
    return _json(result)


# ── Lookup helpers ────────────────────────────────────────────


@mcp.tool()
async def lookup_event(event_ticker: str) -> str:
    """Look up event metadata (sources, settlement info, etc.).

    Args:
        event_ticker: The event ticker identifier.
    """
    result = await _get_client().get_event_metadata(event_ticker)
    return _json(result)


# ── Portfolio (authenticated) ─────────────────────────────────


@mcp.tool()
async def get_balance() -> str:
    """Get account balance and portfolio value (in cents)."""
    result = await _get_client().get_balance()
    return _json(result)


@mcp.tool()
async def get_positions(
    limit: int | None = None,
    cursor: str | None = None,
    ticker: str | None = None,
    event_ticker: str | None = None,
    count_filter: str | None = None,
) -> str:
    """Get current open positions.

    Args:
        limit: Results per page (max 1000).
        cursor: Pagination cursor from a previous response.
        ticker: Filter by market ticker.
        event_ticker: Filter by event ticker.
        count_filter: Filter by non-zero fields: position, total_traded.
    """
    result = await _get_client().get_positions(
        limit=limit,
        cursor=cursor,
        ticker=ticker,
        event_ticker=event_ticker,
        count_filter=count_filter,
    )
    return _json(result)


@mcp.tool()
async def get_orders(
    ticker: str | None = None,
    event_ticker: str | None = None,
    min_ts: int | None = None,
    max_ts: int | None = None,
    status: str | None = None,
    limit: int | None = None,
    cursor: str | None = None,
) -> str:
    """List orders with optional filters.

    Args:
        ticker: Filter by market ticker.
        event_ticker: Filter by event ticker.
        min_ts: Filter orders after this Unix timestamp.
        max_ts: Filter orders before this Unix timestamp.
        status: Filter by status: resting, canceled, executed.
        limit: Results per page (max 1000).
        cursor: Pagination cursor from a previous response.
    """
    result = await _get_client().get_orders(
        ticker=ticker,
        event_ticker=event_ticker,
        min_ts=min_ts,
        max_ts=max_ts,
        status=status,
        limit=limit,
        cursor=cursor,
    )
    return _json(result)


@mcp.tool()
async def create_order(
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
) -> str:
    """Place a new order on a market.

    Args:
        ticker: Market ticker to trade.
        side: Contract side: "yes" or "no".
        action: Order action: "buy" or "sell".
        count: Number of contracts.
        order_type: Order type: "limit" or "market".
        yes_price: Yes-side price in cents (1-99). Required for limit orders on yes side.
        no_price: No-side price in cents (1-99). Required for limit orders on no side.
        client_order_id: Optional client-specified order ID.
        time_in_force: Time in force: fill_or_kill, good_till_canceled, immediate_or_cancel.
        expiration_ts: Expiration Unix timestamp in milliseconds.
    """
    result = await _get_client().create_order(
        ticker=ticker,
        side=side,
        action=action,
        count=count,
        order_type=order_type,
        yes_price=yes_price,
        no_price=no_price,
        client_order_id=client_order_id,
        time_in_force=time_in_force,
        expiration_ts=expiration_ts,
    )
    return _json(result)


@mcp.tool()
async def cancel_order(order_id: str) -> str:
    """Cancel an existing order.

    Args:
        order_id: The order ID to cancel.
    """
    result = await _get_client().cancel_order(order_id)
    return _json(result)


@mcp.tool()
async def get_fills(
    ticker: str | None = None,
    order_id: str | None = None,
    min_ts: int | None = None,
    max_ts: int | None = None,
    limit: int | None = None,
    cursor: str | None = None,
) -> str:
    """Get trade fill history.

    Args:
        ticker: Filter by market ticker.
        order_id: Filter by order ID.
        min_ts: Filter fills after this Unix timestamp.
        max_ts: Filter fills before this Unix timestamp.
        limit: Results per page (max 1000).
        cursor: Pagination cursor from a previous response.
    """
    result = await _get_client().get_fills(
        ticker=ticker,
        order_id=order_id,
        min_ts=min_ts,
        max_ts=max_ts,
        limit=limit,
        cursor=cursor,
    )
    return _json(result)


@mcp.tool()
async def get_settlements(
    ticker: str | None = None,
    event_ticker: str | None = None,
    min_ts: int | None = None,
    max_ts: int | None = None,
    limit: int | None = None,
    cursor: str | None = None,
) -> str:
    """Get settlement history.

    Args:
        ticker: Filter by market ticker.
        event_ticker: Filter by event ticker.
        min_ts: Filter settlements after this Unix timestamp.
        max_ts: Filter settlements before this Unix timestamp.
        limit: Results per page (max 1000).
        cursor: Pagination cursor from a previous response.
    """
    result = await _get_client().get_settlements(
        ticker=ticker,
        event_ticker=event_ticker,
        min_ts=min_ts,
        max_ts=max_ts,
        limit=limit,
        cursor=cursor,
    )
    return _json(result)


def main() -> None:
    """Run the Kalshi MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
