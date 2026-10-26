import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import (
    HumanInTheLoopMiddleware,
    ModelFallbackMiddleware,
    PIIMiddleware,
)
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

load_dotenv()


def openrouter(name):
    return init_chat_model(
        f"openrouter:{name}",
        temperature=0.1, timeout=30_000, max_tokens=300,
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )


# This model doesn't exist, so every call fails: our "provider outage"
main_model = openrouter("google/gemini-offline")
backup_model = openrouter("google/gemini-3.5-flash-lite")


@tool
def refund_order(order_id: int, amount_tl: float) -> str:
    """Refund money for an order to the customer's card."""
    print(f"  [refund_order] refunded {amount_tl} TL for order {order_id}")
    return f"Refund of {amount_tl} TL for order {order_id} is done."

agent = create_agent(
    model=main_model,
    tools=[refund_order],
    system_prompt="You are a support agent for an online clothing store.",
    middleware=[
        PIIMiddleware("credit_card", strategy="redact"),
        ModelFallbackMiddleware(backup_model),
        HumanInTheLoopMiddleware(interrupt_on={"refund_order": True}),
    ],
    checkpointer=InMemorySaver(),  # keeps the paused run until the human decides
)

config = {"configurable": {"thread_id": "customer-42"}}

question = ("My card 4111 1111 1111 1111 was charged twice for order 1042. "
            "Please refund the extra 1250 TL.")

print(f"Customer: {question}\n")

# 1) Run until the agent wants to refund, then pause
result = agent.invoke({"messages": [{"role": "user", "content": question}]}, config)

print(f"PIIMiddleware      the model saw: {result['messages'][0].content!r}")
ai = result["messages"][-1]
print(f"ModelFallback      main model failed, answered by: {ai.response_metadata.get('model_name')}")

call = result["__interrupt__"][0].value["action_requests"][0]
print(f"HumanInTheLoop     paused before {call['name']}({call['args']})")
