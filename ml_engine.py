def detect_jurisdiction(text):
    text = text.lower()

    keywords = ["paypal", "bitcoin", "server", "gmail", "binance", "telegram"]

    for k in keywords:
        if k in text:
            return "INTERNATIONAL (MLAT REQUIRED)"

    return "LOCAL (INDIA)"
