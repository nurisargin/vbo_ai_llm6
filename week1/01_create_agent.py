from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv

load_dotenv()

def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


model = init_chat_model(
    model="openrouter:google/gemini-2.5-flash",
    max_tokens=200,
)

agent = create_agent(
    model=model,
    system_prompt="You are a helpful assistant",
    tools=[get_weather],
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "Where is the capital of France?"}]}
)

print(result)