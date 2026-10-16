
from semantic_router import Route, IndexedRouter
from semantic_router.encoders import HuggingFaceEncoder

encoder = HuggingFaceEncoder(
    name="sentence-transformers/all-MiniLM-L6-v2"
)

faq = Route(
    name="faq",
    utterances=[
        "What is the return policy of the products?",
        "Do I get discount with the HDFC credit card?",
        "How can I track my order?",
        "What payment methods are accepted?",
        "How long does it take to process a refund?",
    ],
)

sql = Route(
    name="sql",
    utterances=[
        "I want to buy Nike shoes that have 50% discount.",
        "Are there any shoes under Rs. 3000?",
        "Do you have formal shoes in size 9?",
        "Are there any Puma shoes on sale?",
        "What is the price of Puma running shoes?",
    ],
)

router = IndexedRouter(
    routes=[faq, sql],
    encoder=encoder,
)

if __name__ == "__main__":
    result1 = router("What is your policy on defective product?")
    print(result1.name if result1 else "No route found")

    result2 = router("Pink Puma shoes in price range 5000 to 1000")
    print(result2.name if result2 else "No route found")
