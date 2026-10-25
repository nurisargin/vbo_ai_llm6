import asyncio
import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_mcp_adapters.client import MultiServerMCPClient


load_dotenv()

model = init_chat_model(
    "openrouter:google/gemini-3.5-flash-lite",
    temperature=0.1, timeout=30_000, max_tokens=500,
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

client = MultiServerMCPClient({
    "currency": {
        "transport": "streamable_http",
        "url": "http://localhost:8001/mcp",
    }
})


async def main():
    # Ask the server which tools it has; they come back as LangChain tools
    tools = await client.get_tools()
    limited_tools = []
    print("Tools from the MCP server:", [t.name for t in tools])

    agent = create_agent(model, tools)
    result = await agent.ainvoke(
    {"messages": [{"role": "user", "content":
        "Check tables in customer databse"}]}
    )

    for msg in result["messages"]:
        msg.pretty_print()

asyncio.run(main())