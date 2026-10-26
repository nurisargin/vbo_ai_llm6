"""
Six middleware hook points demo.

A customer asks a store assistant where their order is. The agent has to
call a shipping API, and the API times out on the first try. Each of the
six hooks does one small, real job along the way:

    before_agent      record the start time when the customer's message arrives
      before_model    show what new information the model is about to see
        wrap_model_call   time each model call and count its tokens
      after_model     show what the model decided: use a tool, or answer
        wrap_tool_call    retry the shipping API when it times out
      ...the agent loops back to the model until it answers...
    after_agent       print the bill: time, model calls, tokens

The agent loop itself never changes; middleware adds behavior around it.

Run:
    uv run python week_03/02_middleware/main1_hooks_example.py
"""

import time
from langchain.tools import tool
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.agents.middleware import (
    before_agent,
    before_model,
    after_model,
    after_agent,
    wrap_model_call,
    wrap_tool_call,
)
from dotenv import load_dotenv
import os

load_dotenv()

model = init_chat_model(
    "openrouter:google/gemini-3.5-flash-lite",
    temperature=0.1, timeout=30_000, max_tokens=500,
    api_key=os.getenv("OPENROUTER_API_KEY"),
)


api_calls = 0

@tool
def track_order(order_id: int) -> str:
    """Look up where an order is with the shipping company."""
    global api_calls
    api_calls += 1
    if api_calls == 1:
        raise TimeoutError("shipping API did not respond")  # flaky on purpose
    return f"Order {order_id}: in Ankara distribution center, delivery on Friday"

stats = {"start": 0.0, "model_calls": 0, "model_seconds": 0.0, "tokens": 0}


@before_agent
def record_start_time(state, runtime):
    stats["start"] = time.time()
    print(f"[before_agent]     Customer: {state['messages'][-1].content!r}")


@before_model
def show_new_info(state, runtime):
    last = state["messages"][-1]
    if last.type == "tool":
        print(f"[before_model]     The model now also sees the tool result: {last.content!r}")
    else:
        print(f"[before_model]     The model sees the customer's question")


@after_model
def show_decision(state, runtime):
    reply = state["messages"][-1]
    if reply.tool_calls:
        call = reply.tool_calls[0]
        print(f"[after_model]      Decision: I need data, call {call['name']}({call['args']})")
    else:
        print(f"[after_model]      Decision: I have what I need, answer the customer")

@after_agent
def print_bill(state, runtime):
    total = time.time() - stats["start"]
    print(f"\n[after_agent]      Done in {total:.1f}s: {stats['model_calls']} model calls "
          f"({stats['model_seconds']:.1f}s), {stats['tokens']} tokens")


@wrap_model_call
def time_and_count(request, handler):
    t0 = time.time()
    response = handler(request)  # the real model call
    seconds = time.time() - t0
    usage = response.result[-1].usage_metadata or {}
    stats["model_calls"] += 1
    stats["model_seconds"] += seconds
    stats["tokens"] += usage.get("total_tokens", 0)
    print(f"[wrap_model_call]  Model call took {seconds:.1f}s, "
          f"{usage.get('total_tokens', 0)} tokens")
    return response


@wrap_tool_call
def retry_on_timeout(request, handler):
    for attempt in (1,2):
        try:
            result = handler(request)  # the real tool call
            if attempt > 3:
                print(f"[wrap_tool_call]   Attempt {attempt} worked")
            return result
        except TimeoutError as e:
            print(f"[wrap_tool_call]   Attempt {attempt} failed ({e}), retrying...")
    raise TimeoutError("shipping API is down")


agent = create_agent(
    model=model,
    tools=[track_order],
    system_prompt="You are a friendly store assistant. Keep answers short.",
    middleware=[
        record_start_time, # befare_agent
        show_new_info, # before_model
        time_and_count, # wrap_model_call
        show_decision, # after_model
        retry_on_timeout, # wrap_tool_call
        print_bill, # after_agent
    ],
)


result = agent.invoke({"messages": [{"role": "user", "content": "Where is my order 1042?"}]})
print(result)
print(f"\nAssistant: {result['messages'][-1].content}")