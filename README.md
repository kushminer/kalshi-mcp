# kalshi-mcp

An MCP (Model Context Protocol) server that wraps the [Kalshi](https://kalshi.com) prediction market API. This lets Claude (or any MCP client) browse markets, check prices, manage portfolios, and place trades on Kalshi.

## Prerequisites

- Python 3.10+
- A Kalshi account with an API key and RSA private key ([how to create one](https://kalshi.com/account/api-keys))

## Installation

```bash
pip install -e .
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv pip install -e .
```

## Configuration

Set these environment variables:

| Variable | Required | Description |
|----------|----------|-------------|
| `KALSHI_API_KEY` | Yes | Your Kalshi API key ID |
| `KALSHI_PRIVATE_KEY_PATH` | Yes | Path to your RSA private key PEM file |
| `KALSHI_API_BASE_URL` | No | API base URL (default: `https://api.elections.kalshi.com/trade-api/v2`) |

For the demo/sandbox environment, set `KALSHI_API_BASE_URL` to `https://demo-api.kalshi.co/trade-api/v2`.

## Usage with Claude Code

Add to your Claude Code MCP config (`~/.claude/claude_desktop_config.json` or project `.mcp.json`):

```json
{
  "mcpServers": {
    "kalshi": {
      "command": "kalshi-mcp",
      "env": {
        "KALSHI_API_KEY": "your-api-key",
        "KALSHI_PRIVATE_KEY_PATH": "/absolute/path/to/private-key.pem"
      }
    }
  }
}
```

> **Note:** If `kalshi-mcp` is not on your shell's PATH, use the full path (e.g. `/opt/miniconda3/bin/kalshi-mcp`). You can find it with `which kalshi-mcp`.

## Available Tools

### Market Data

| Tool | Description |
|------|-------------|
| `get_exchange_status` | Exchange trading status |
| `get_exchange_schedule` | Exchange schedule |
| `get_events` | List events with filters (status, series, pagination) |
| `get_event` | Single event with optional nested markets |
| `get_markets` | List markets with filters |
| `get_market` | Single market details |
| `get_market_orderbook` | Orderbook for a market |
| `get_trades` | Recent trades (optional ticker filter) |
| `get_market_candlesticks` | OHLCV candlestick data |
| `get_series` | Series metadata |
| `lookup_event` | Event metadata (sources, settlement info) |

### Portfolio (authenticated)

| Tool | Description |
|------|-------------|
| `get_balance` | Account balance and portfolio value |
| `get_positions` | Current open positions |
| `get_orders` | List orders with filters |
| `create_order` | Place a new order (limit or market) |
| `cancel_order` | Cancel an order by ID |
| `get_fills` | Trade fill history |
| `get_settlements` | Settlement history |

## Development

Run the MCP inspector for interactive testing:

```bash
KALSHI_API_KEY=your-key KALSHI_PRIVATE_KEY_PATH=/path/to/key.pem mcp dev src/kalshi_mcp/server.py
```

## License

MIT
