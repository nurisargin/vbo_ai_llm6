from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv

load_dotenv()

def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

def get_time(city: str) -> str:
    """Get time for a given city."""
    return f"The local time in {city} is 17:30 (5:30 PM)."

def convert_currency(amount: float, rate: float) -> str:
    """Convert an amount using a given exchange rate."""
    return f"{amount} € x {rate} = **{amount * rate} USD***."

model = init_chat_model(
    model="openrouter:google/gemini-2.5-flash",
    max_tokens = 100,
)

agent = create_agent(
    model = model,
    system_prompt = "You are a helpful assistant.",
    tools=[get_weather, get_time, convert_currency],
)

def ask_agent(question: str) -> str:
    result = agent.invoke(
        {"messages": [{"role": "user", "content": question}]}
    )
    return result["messages"][-1].content


#Task 1 — A second tool: Ask the agent a question about What's the weather and the local time in Istanbul
city="Istanbul"
ai_message = ask_agent(f"What's the weather and the local time in {city}?")

print(f"=== Task 1 ===\nHere’s the current information for {city}:")
print(ai_message)

#Task 2 — A tool that actually computes something
amount = 100
exchange_rate = 1.12
ai_message = ask_agent(f"I have {amount} euros and the rate is {exchange_rate} — how many dollars is that?")

print("=== Task 2 ===")
print(ai_message)