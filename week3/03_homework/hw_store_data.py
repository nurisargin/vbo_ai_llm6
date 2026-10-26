"""
Sample data for the week 3 homework: an online clothing store's orders
and six customer emails from its support inbox.

Import it in your solution:
    from store_data import ORDERS, PRODUCTS, EMAILS
"""

# What the store's order system knows. Your tools read from here.
ORDERS = {
    1042: {"customer": "Ayşe Yılmaz", "items": "2 x winter jacket (L)",
           "total_tl": 2500.00, "status": "delivered"},
    1043: {"customer": "Mehmet Kaya", "items": "1 x wool scarf",
           "total_tl": 349.90, "status": "in transit, arrives Friday"},
    1045: {"customer": "Zeynep Demir", "items": "1 x rain boots (38)",
           "total_tl": 899.90, "status": "in transit, arrives Monday"},
    1050: {"customer": "Can Öztürk", "items": "1 x down coat (XL)",
           "total_tl": 4200.00, "status": "delayed at the warehouse"},
}

# What the store's product catalog knows.
PRODUCTS = {
    "winter jacket": {"sizes": "S, M, L", "price_tl": 1250.00,
                      "material": "water-resistant shell (not waterproof), down filling"},
    "wool scarf": {"sizes": "one size", "price_tl": 349.90, "material": "100% wool"},
    "rain boots": {"sizes": "36-41", "price_tl": 899.90, "material": "waterproof rubber"},
}

# The inbox. Each email is a plain string, exactly as the customer wrote it.
EMAILS = [
    # 1. A simple question about an order
    "Hello, I ordered a scarf last week (order 1043). Could you tell me "
    "when it will arrive? Thanks, Mehmet",

    # 2. Wrong size, wants money back, and pastes a card number
    "hi, this is ayşe yılmaz. order #1042, one of the jackets came in M "
    "but i ordered L. please refund that jacket, it was 1.250,00 TL, to "
    "my card 4111 1111 1111 1111.",

    # 3. Wants money back for an order that hasn't arrived yet
    "Hi, I found the same rain boots cheaper somewhere else. Please cancel "
    "order 1045 and refund the 899,90 TL. Thanks, Zeynep Demir",

    # 4. Angry: the order is late and nobody answered
    "This is the THIRD time I am writing about order 1050!!! The coat was "
    "supposed to arrive two weeks ago and nobody answers me. Absolutely "
    "unacceptable, I will never shop here again.",

    # 5. A product question, no order involved
    "Hi! Does the winter jacket also come in XL? And is it waterproof?",

    # 6. Not a customer at all
    "Congratulations!!! You have been selected for a FREE iPhone. Click "
    "the link and enter your bank details to claim your prize.",
]
