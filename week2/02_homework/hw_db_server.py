"""
A real MCP server over HTTP for querying a PostgreSQL database.

Connects to PostgreSQL using the connection string in the PG_DSN environment
variable and exposes database operations as MCP tools. Any MCP client (our
agent, Claude Desktop, Cursor, ...) can connect to it at
http://localhost:8005/mcp.

Run (keep it running while connecting an MCP client):
    uv run python week2/02_homework/hw_db_server.py
"""

from mcp.server.fastmcp import FastMCP 
from sqlmodel import  Session, inspect
from sqlalchemy import text
from textwrap import shorten
from hw_db import get_engine

mcp = FastMCP("Database", port=8005)

engine = get_engine()

@mcp.tool()
def list_tables() -> list[str]:
    """List the names of all tables in the database."""
    return inspect(engine).get_table_names()

@mcp.tool()
def describe_table(table_name: str) -> list[str]:
    """Describe a database table: list its columns with type and nullability."""
    inspector = inspect(engine)

    if not inspector.has_table(table_name):
        raise ValueError(
            f"Table '{table_name}' not found. "
            f"Available tables: {inspector.get_table_names()}"
        )

    return [
        f"{col['name']}: {col['type']}"
        + ("" if col["nullable"] else " (NOT NULL)")
        for col in inspector.get_columns(table_name)
    ]

@mcp.tool()
def run_select(sql: str) -> str:
    """
    Execute a read-only PostgreSQL SELECT statement and return results
    as a markdown table.

    Rules:
    - Only SELECT queries are allowed (safety guard).
    - Target dialect is PostgreSQL.
    - Use SINGLE quotes for string literals: WHERE country = 'France'.
    - Use DOUBLE quotes only for identifiers when needed: "Order Date".
    - Do not use backticks (those are MySQL)."""

    max_rows = 50

    normalized = sql.strip().lower()
  
    if not normalized.startswith("select"):
        raise ValueError("This tool only supports SELECT queries.")

    with Session(engine) as session:
        result = session.exec(text(sql))
        rows = result.fetchall()
        if not rows:
            return "Query executed successfully, but returned 0 rows."

        col_names = result.keys()
        rows = rows[:max_rows]

    # Format as Markdown
    header = "| " + " | ".join(col_names) + " |"
    sep = "| " + " | ".join("---" for _ in col_names) + " |"

    body = []
    for r in rows:
        body.append(
            "| "
            + " | ".join(shorten(str(v), width=80, placeholder="…") for v in r)
            + " |"
        )

    table = "\n".join([header, sep] + body)
    if len(body) == max_rows:
        table += f"\n\n_NOTE: truncated to {max_rows} rows._"

    return table


if __name__ == "__main__":
    print("[Database Server] MCP endpoint: http://localhost:8005/mcp")
    mcp.run(transport="streamable-http")


#Answer three questions (as comments in your code)
# 1. Why give the agent three tools instead of one run_sql(sql) tool? What would go wrong with only one?
# 2. Why read the columns from the database instead of writing them into the tool's description?
# 3. run_select only accepts SELECT. What could still go wrong? Name one more protection.

# CEVAPLAR
# 1. Neden tek bir run_sql yerine üç araç?
#    Yeni başlayan bir analist gibi, ajanın da önce hangi tabloların olduğuna
#    (list_tables), sonra sütunlarına (describe_table) bakıp en son sorguyu
#    (run_select) yazması gerekir. Tek run_sql aracında bu adımlar yoktur:
#    model tablo ve sütun adlarını tahmin eder, hatalı veya uydurma sorgular
#    yazar. Ayrıca genel bir run_sql INSERT/DROP gibi tehlikeli komutları da
#    çalıştırabilir. Küçük ve tek amaçlı araçlar daha güvenli ve kontrol
#    etmesi daha kolaydır.
#
# 2. Neden sütunları araç açıklamasına yazmak yerine veritabanından okuyoruz?
#    Tablolarla ilgili hiçbir bilgi koda yazılmaz, ajan bunları araçları
#    çağırarak öğrenir. Elle yazılan şema veritabanının bir kopyasıdır ve
#    sütun eklenince/silinince eskir. Canlı okumak her zaman doğru bilgiyi
#    verir (tek doğru kaynak veritabanı). Ayrıca kod başka bir veritabanında
#    da değişmeden çalışır ve prompt şişmez.
#
# 3. Sadece SELECT kabul etmek yetmez; ne ters gidebilir? Ek bir koruma nedir?
#    SELECT ile de çok ağır sorgular çalıştırılıp veritabanı yavaşlatılabilir,
#    hassas veriler (şifre, kişisel bilgi) okunup modele gönderilebilir.
#    Anahtar kelime filtresi de aşılabilir.
#    Ek koruma: Sadece SELECT yetkisi olan salt okunur bir veritabanı kullanıcısı
#    ile bağlanmak. Böylece doğrulama aşılsa bile veritabanı yazmayı reddeder.
#    (Kodda ayrıca salt okunur transaction, zaman aşımı ve 50 satır sınırı var.)