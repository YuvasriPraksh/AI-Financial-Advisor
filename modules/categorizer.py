"""
categorizer.py - Automatic Expense Categorization
Maps merchants and keywords to expense categories.
"""

# ---------------------------------------------------------------------------
# Category keyword mapping (easily extendable)
# ---------------------------------------------------------------------------
CATEGORY_KEYWORDS = {
    "Food": [
        "swiggy", "zomato", "dominos", "domino", "pizza hut", "kfc",
        "mcdonald", "burger king", "starbucks", "ccd", "cafe", "restaurant",
        "hotel", "dhaba", "biryani", "haldiram", "barbeque", "barbeque nation",
        "box8", "freshmenu", "licious", "eatfit", "faasos", "behrouz",
        "the good bowl", "wow momo", "subway", "dunkin", "bakery", "food",
        "meal", "lunch", "dinner", "breakfast", "snack", "grocery",
    ],
    "Transport": [
        "uber", "ola", "rapido", "meru", "taxi", "auto", "cab",
        "indigo", "spicejet", "airindia", "vistara", "goair", "akasa",
        "irctc", "railway", "metro", "bus", "redbus", "abhibus",
        "petrol", "diesel", "fuel", "parking", "toll", "fastag",
        "transport", "travel", "flight", "train", "makemytrip",
        "yatra", "cleartrip", "goibibo",
    ],
    "Shopping": [
        "amazon", "flipkart", "myntra", "meesho", "nykaa", "ajio",
        "snapdeal", "shoppers stop", "lifestyle", "max fashion",
        "reliance", "dmart", "bigbasket", "blinkit", "grofers", "dunzo",
        "zepto", "jiomart", "spencer", "more", "star bazaar",
        "decathlon", "croma", "vijay sales", "tata cliq", "paytm mall",
        "shopping", "purchase", "order",
    ],
    "Entertainment": [
        "netflix", "amazon prime", "hotstar", "disney", "zee5", "sonyliv",
        "voot", "mx player", "youtube premium", "spotify", "gaana",
        "jiosaavn", "wynk", "apple music", "bookmyshow", "pvr", "inox",
        "cinepolis", "carnival", "gaming", "steam", "epic games",
        "entertainment", "movie", "cinema", "concert", "event",
    ],
    "Bills": [
        "electricity", "bescom", "msedcl", "tpddl", "cesc", "bses",
        "water", "gas", "lpg", "indane", "hp gas", "bharatgas",
        "broadband", "wifi", "internet", "airtel", "jio", "bsnl",
        "vi", "vodafone", "idea", "mobile recharge", "recharge",
        "emi", "loan", "insurance", "lic", "hdfc life", "sbi life",
        "bajaj", "max life", "rent", "maintenance", "society",
        "bill", "utility", "subscription",
    ],
    "Healthcare": [
        "pharmacy", "medplus", "apollo pharmacy", "1mg", "netmeds",
        "pharmeasy", "medlife", "clinikk", "portea", "practo",
        "doctor", "hospital", "clinic", "diagnostic", "pathology",
        "health", "medicine", "medical", "ayurvedic", "dental",
        "optical", "eye care", "fitness", "gym", "cult fit",
    ],
    "Education": [
        "udemy", "coursera", "byjus", "unacademy", "vedantu",
        "upgrad", "simplilearn", "edx", "skillshare", "linkedin learning",
        "book", "stationery", "pen", "notebook", "college", "school",
        "university", "tuition", "coaching", "exam", "education",
        "course", "training", "certification",
    ],
}

DEFAULT_CATEGORY = "Others"


def categorize(merchant: str, raw_text: str = "") -> str:
    """
    Determine the category of an expense.

    Checks the merchant name first, then falls back to scanning
    the raw OCR text for known keywords.

    Args:
        merchant:  Detected merchant/app name.
        raw_text:  Full OCR text from the screenshot (optional).

    Returns:
        str: One of the predefined category names.
    """
    combined = (merchant + " " + raw_text).lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in combined:
                return category

    return DEFAULT_CATEGORY


def get_all_categories() -> list:
    """Return the list of all available category names."""
    return list(CATEGORY_KEYWORDS.keys()) + [DEFAULT_CATEGORY]


def add_keyword(category: str, keyword: str) -> bool:
    """
    Dynamically add a keyword to an existing category.
    Returns True on success, False if category not found.
    """
    if category in CATEGORY_KEYWORDS:
        CATEGORY_KEYWORDS[category].append(keyword.lower())
        return True
    return False
