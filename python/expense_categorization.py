"""
Expense Categorization Module
-----------------------------
Implements rule-based keyword classification, refund recognition,
and explicit taxonomy assignment. Adheres strictly to the requirement
that unclassifiable records receive 'Uncategorised' rather than an
arbitrary category.
"""

from typing import Dict, List, Optional, Tuple
import re

# Standard Category Taxonomy
STANDARD_CATEGORIES: List[str] = [
    "Salary",
    "Food & Dining",
    "Transportation",
    "Shopping",
    "Education",
    "Healthcare",
    "Entertainment",
    "Housing",
    "Utilities",
    "Travel",
    "Other",
    "Uncategorised",
]

# Keyword dictionary mapping to standard categories
CATEGORY_KEYWORD_RULES: Dict[str, List[str]] = {
    "Salary": [
        "salary", "payroll", "monthly stipend", "consulting fee", "freelance payout",
        "dividend", "interest credited", "bonus payout", "incentive"
    ],
    "Food & Dining": [
        "swiggy", "zomato", "mcdonald", "starbucks", "domino", "pizza", "burger",
        "restaurant", "cafe", "dine", "supermarket", "grocery", "bigbasket",
        "blinkit", "zepto", "dmart", "bakery", "subway", "kfc", "chai point", "haldiram"
    ],
    "Transportation": [
        "uber", "ola", "metro", "fuel", "petrol", "diesel", "shell", "hpcl", "bpcl",
        "iocle", "auto", "irctc", "bus ticket", "parking", "fastag", "toll", "rapido"
    ],
    "Shopping": [
        "amazon", "flipkart", "myntra", "ajio", "zara", "h&m", "retail", "croma",
        "reliance digital", "lifestyle", "apparel", "ikea", "electronics", "decathlon",
        "marks & spencer", "westside"
    ],
    "Education": [
        "coursera", "udemy", "university", "tuition", "books", "college", "institute",
        "certification", "exam fee", "edx", "skillshare", "hcl training"
    ],
    "Healthcare": [
        "pharmacy", "apollo", "hospital", "clinic", "1mg", "pharmeasy", "doctor",
        "dental", "diagnostics", "lab test", "medicine", "max healthcare", "opticals"
    ],
    "Entertainment": [
        "netflix", "spotify", "hotstar", "prime video", "cinema", "pvr", "inox",
        "movie ticket", "concert", "steam", "playstation", "bookmyshow", "gaming"
    ],
    "Housing": [
        "house rent", "apartment rent", "society maintenance", "brokerage", "lease",
        "property tax", "home maintenance", "painting", "plumbing"
    ],
    "Utilities": [
        "electricity bill", "bescom", "tneb", "water bill", "piped gas", "broadband",
        "wifi", "airtel", "jio fiber", "mobile recharge", "cylinder", "indane", "dth"
    ],
    "Travel": [
        "flight", "hotel", "airbnb", "makemytrip", "booking.com", "resort", "indigo",
        "air india", "vistara", "cleartrip", "goibibo", "expedia", "luggage"
    ],
    "Other": [
        "donation", "gift", "charity", "miscellaneous", "cash withdrawal", "atm"
    ]
}

# Refund indicator keywords
REFUND_KEYWORDS: List[str] = [
    "refund", "reversal", "reimbursed", "reimbursement", "cashback", "returned goods",
    "chargeback", "cancelled order refund"
]


def is_refund_description(description: str) -> bool:
    """Check if the transaction description indicates a refund or reversal."""
    if not isinstance(description, str):
        return False
    desc_lower = description.lower()
    return any(keyword in desc_lower for keyword in REFUND_KEYWORDS)


def classify_transaction(
    description: str,
    raw_category: Optional[str] = None,
    txn_type: Optional[str] = None
) -> Tuple[str, str]:
    """
    Classifies a transaction into a category and transaction type.
    
    Returns:
        Tuple of (Category, TransactionType)
        Category: Standard Category or 'Uncategorised'
        TransactionType: 'INCOME', 'EXPENSE', or 'REFUND'
    """
    if not isinstance(description, str):
        return "Uncategorised", "EXPENSE"

    desc_clean = description.strip()
    desc_lower = desc_clean.lower()

    # 1. Determine if this is a refund
    if (txn_type and txn_type.upper() == "REFUND") or is_refund_description(desc_clean):
        detected_type = "REFUND"
    elif (txn_type and txn_type.upper() == "INCOME"):
        detected_type = "INCOME"
    elif any(k in desc_lower for k in CATEGORY_KEYWORD_RULES["Salary"]):
        detected_type = "INCOME"
    else:
        detected_type = "EXPENSE"

    # 2. Check if user/source provided a recognized valid category
    if raw_category and isinstance(raw_category, str):
        cleaned_cat = raw_category.strip()
        for valid_cat in STANDARD_CATEGORIES:
            if cleaned_cat.lower() == valid_cat.lower():
                return valid_cat, detected_type

    # 3. Match against keyword rules
    # Check income first if detected as income
    if detected_type == "INCOME":
        for kw in CATEGORY_KEYWORD_RULES["Salary"]:
            if kw in desc_lower:
                return "Salary", "INCOME"
        return "Salary", "INCOME"

    # For expenses and refunds, find the matching expense category
    for category, keywords in CATEGORY_KEYWORD_RULES.items():
        if category == "Salary":
            continue
        for kw in keywords:
            # Word boundary or substring match
            pattern = r'\b' + re.escape(kw) + r'\b'
            if re.search(pattern, desc_lower) or kw in desc_lower:
                return category, detected_type

    # 4. Strict Fallback: Never assign a false category silently
    return "Uncategorised", detected_type


def override_category(
    df,
    transaction_id: str,
    new_category: str
):
    """Allows manual correction of an individual transaction category."""
    if new_category not in STANDARD_CATEGORIES:
        raise ValueError(f"Category '{new_category}' is not in standard taxonomy: {STANDARD_CATEGORIES}")
    
    idx = df[df["transaction_id"] == transaction_id].index
    if len(idx) == 0:
        raise KeyError(f"Transaction ID {transaction_id} not found.")
    
    df.loc[idx, "category"] = new_category
    return df
