"""
Custom middleware demo: two fixes from a production support chatbot.

A store assistant can look up a customer's orders. Each middleware fixes
a problem the real chatbot had:

  1. use_real_customer_id  (after_model)     the model passes whatever customer
                                             ID it was given; we overwrite it
                                             with the logged-in customer's ID
  2. keep_answers_short    (wrap_model_call) answers were far too long; we add
                                             a note to each model call only

See 03_custom_middleware.md for the story behind each one, and for a third
one (RepeatedToolCallGuard) that only fires when something goes wrong.

Run:
    uv run python week_03/02_middleware/main3_custom_example.py
"""

import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import after_model, wrap_model_call
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage
from langchain.tools import tool

load_dotenv()

model = init_chat_model(
    "openrouter:google/gemini-3.5-flash-lite",
    temperature=0.1, timeout=30_000, max_tokens=500,
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

SESSION_CUSTOMER_ID = "cus_8f2a"  # comes from the login, never from the model

ORDERS = {
    "cus_8f2a": "Order 1042: blue jacket, arrives Friday",
    "cus_77c1": "Order 0998: wedding dress, delivered",  # another customer!
}

@tool
def get_orders(customer_id: str) -> str:
    """List a customer's orders."""
    return ORDERS.get(customer_id, "No orders found")

# ── 1. Fix IDs after the model writes the tool call ─────────────────────────
@after_model
def use_real_customer_id(state, runtime):
    reply = state["messages"][-1]
    if not reply.tool_calls:
        return None
    fixed = []
    for call in reply.tool_calls:
        given = call["args"].get("customer_id")
        if given and given != SESSION_CUSTOMER_ID:
            print(f"  [use_real_customer_id] model sent {given!r}, "
                  f"replaced with the logged-in customer {SESSION_CUSTOMER_ID!r}")
            call = {**call, "args": {**call["args"], "customer_id": SESSION_CUSTOMER_ID}}
        fixed.append(call)
    # Same message id, so this replaces the model's message instead of adding one
    return {"messages": [reply.model_copy(update={"tool_calls": fixed})]}

# ── 2. A note for this model call only, never saved to history ──────────────
@wrap_model_call
def keep_answers_short(request, handler):
    note = HumanMessage("Answer only what was asked, in at most 2 sentences.")
    return handler(request.override(messages=[*request.messages, note]))

tools = [get_orders]

system_prompt = "You are a store assistant."
agent = create_agent(
    model, tools=tools, 
    system_prompt=system_prompt,
    middleware=[use_real_customer_id, keep_answers_short],
)
# 
# def ask(agent, question):
#     print(f"\nCustomer: {question}")
#     result = agent.invoke({"messages": [{"role": "user", "content": question}]})
#     answer = result["messages"][-1].content
#     short = answer if len(answer) < 300 else answer[:300] + " ..."
#     print(f"Assistant ({len(answer)} chars): {short}")

# print("=" * 70, "\nDemo 1: a customer asks for someone else's orders\n", "=" * 70, sep="")
# ask(agent, "Show the orders for customer cus_77c1.")    

result = agent.invoke({"messages": [{"role": "user", "content": "Show the orders for customer cus_77c1."}]})

print(result)