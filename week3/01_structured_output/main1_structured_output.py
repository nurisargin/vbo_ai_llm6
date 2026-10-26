import os
from typing import Literal

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field

load_dotenv()

model = init_chat_model(
    "openrouter:google/gemini-3.5-flash-lite",  # cheap & fast model
    temperature=0.1,      # low temperature → more deterministic answers
    timeout=30_000,       # milliseconds to wait before giving up
    max_tokens=1000,      # max tokens the model is allowed to generate
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

class ProblemItem(BaseModel):
    product: str
    ordered_size: str | None
    received_size: str | None

class SupportTicket(BaseModel):
    customer_name: str
    email: str | None = Field(description="A normal email address, e.g. name@gmail.com")
    # pattern: Pydantic rejects anything else, e.g. "0555 123 45 67" with spaces.
    # ToolStrategy then sends the error back to the model, which tries again.
    phone: str | None = Field(
        pattern=r"^05\d{9}$",
        description="The number the customer wants to be called on, 11 digits, no spaces",
    )
    order_id: int | None
    problem: Literal["wrong_size", "damaged", "late_delivery", "missing_item", "other"]
    wants: Literal["refund", "exchange", "information"]
    item: ProblemItem = Field(description="The one product the problem is about")
    refund_amount_tl: float | None = Field(description="Amount in TL as a plain number")

email = """hi, this is ayşe yılmaz (ayse.y at gmail dot com)
ordered 2 jackets in size L and a scarf last week, order #1042. one of
the jackets came in M!! the scarf is fine. i want my money back for
the wrong jacket, it was Bin ikiyüz elli TL. call me after 6pm on 0555 123 45 67,
actually no that's my old number, use 0532 987 65 43 instead"""

agent = create_agent(
    model=model,
    system_prompt="You turn customer emails into support tickets.",
    response_format=ToolStrategy(SupportTicket),
)

result = agent.invoke({"messages": [{"role": "user", "content": email}]})

ticket = result["structured_response"]

print(ticket.model_dump_json(indent=2))