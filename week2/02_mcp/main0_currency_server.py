"""
A real MCP server over HTTP: live exchange rates.

Wraps the free Frankfurter API (European Central Bank rates, no API key)
and exposes it as MCP tools. Any MCP client (our agent, Claude Desktop,
Cursor, ...) can connect to it at http://localhost:8001/mcp.

Run (keep it running, then start main0_http_agent.py in another terminal):
    uv run python week_02/02_mcp/main0_currency_server.py
"""
import httpx
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("Currency")
API = "https://api.frankfurter.dev/v1"


@mcp.tool()
def get_exchange_rate(base: str, target: str, date: str = "latest") -> str:
    """Get the exchange rate from one currency to another.

    Args:
        base: Currency code to convert from, e.g. "USD"
        target: Currency code to convert to, e.g. "TRY"
        date: "latest" or a past date as YYYY-MM-DD
    """
    data = httpx.get(f"{API}/{date}", params={"base": base, "symbols": target}).json()
    print(f"[Currency Server] {base}->{target} on {data['date']}: {data['rates'][target]}")
    return f"1 {base} = {data['rates'][target]} {target} (date: {data['date']})"


@mcp.tool()
def convert(amount: float, base: str, target: str) -> str:
    """Convert an amount of money between currencies at today's rate."""
    data = httpx.get(f"{API}/latest", params={"base": base, "symbols": target}).json()
    result = round(amount * data["rates"][target], 2)
    print(f"[Currency Server] {amount} {base} = {result} {target}")
    return f"{amount} {base} = {result} {target} (date: {data['date']})"


@mcp.tool()
def get_customer_db_tables(database: str) -> list:
    """Lists database tables."""
    return ['tablea','tableb']

if __name__ == "__main__":
    print("[Currency Server] MCP endpoint: http://localhost:8001/mcp")
    mcp.run(transport="streamable-http", port=8001)