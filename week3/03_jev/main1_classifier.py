import os

from dotenv import load_dotenv
from langchain_typesafe import Choice, Noul, Score, TypeSafeClassifier

load_dotenv()

classifier = TypeSafeClassifier(
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api",
    )

QUESTIONS = {
    # Multiple choice: one label wins, every label gets a probability
    "intent": Choice(
        instructions="What does the customer want?",
        criteria={
            "order_status": "Where is my order, delivery dates, tracking",
            "return_exchange": "Returning or exchanging a product",
            "product_question": "Questions about features, sizes, stock",
        },
    ),
    # Yes/no: a single probability between 0 and 1
    "complaint": Noul(instructions="The customer is complaining about something"),
    # Ordered levels, numbered 0..2 in this order; the score can land in between
    "frustration": Score(
        instructions="How frustrated does the customer appear?",
        criteria=["Calm", "Annoyed but polite", "Very angry"],
    ),
}

r = classifier.invoke({"state": "My order was supposed to arrive last week.", "questions": QUESTIONS})
print(r)