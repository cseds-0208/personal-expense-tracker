"""
Synthetic Financial Dataset Generator
-------------------------------------
Generates an enterprise-scale synthetic dataset of 600+ transactions spanning
multiple calendar months (e.g. Oct 2026 - Dec 2026), incorporating:
- Fixed salary credits and consulting revenue (Income)
- Standard living expenses across diverse categories
- Multiple payment rails (UPI, Credit Card, Debit Card, Net Banking, Cash)
- Legitimate merchant refunds and reversals
- Ambiguous vendor strings that resolve to 'Uncategorised'
- Month-end boundary dates (28th, 29th, 30th, 31st)
- Deliberate data-quality anomalies (duplicates, null date, unparseable amount)
  to thoroughly exercise the data hygiene pipeline.
"""

import os
import random
from datetime import date, timedelta
import pandas as pd

# Set deterministic random seed
random.seed(42)

# Vendors and descriptions mapped by category
MERCHANT_CATALOG = {
    "Salary": [
        ("HCL Technologies Monthly Payroll", 125000.0, 125000.0, ["Net Banking"]),
        ("Freelance Python Architecture Consulting", 18000.0, 45000.0, ["Net Banking", "UPI"]),
        ("Quarterly Mutual Fund Dividend Payout", 3500.0, 8500.0, ["Net Banking"]),
        ("Tech Mentorship Honorarium", 5000.0, 15000.0, ["UPI"]),
    ],
    "Housing": [
        ("Prestige Falcon City Apartment Rent", 22000.0, 22000.0, ["Net Banking"]),
        ("Apartment Maintenance & Security Corpus", 3800.0, 4200.0, ["Net Banking", "UPI"]),
        ("Urban Company Plumbing Repair & Tap Fitting", 650.0, 1500.0, ["UPI", "Credit Card"]),
        ("Society Water & Generator Surcharge", 850.0, 1200.0, ["UPI"]),
    ],
    "Food & Dining": [
        ("Swiggy Gourmet Order - Biryani By Kilo", 450.0, 1350.0, ["UPI", "Credit Card"]),
        ("Zomato Delivery - Mainland China", 620.0, 1800.0, ["UPI", "Credit Card"]),
        ("BigBasket Weekly Organic Produce", 1200.0, 3200.0, ["Credit Card", "Debit Card"]),
        ("Blinkit Express Delivery Grocery", 280.0, 950.0, ["UPI"]),
        ("Zepto 10-min Daily Milk and Eggs", 180.0, 480.0, ["UPI"]),
        ("Starbucks Reserve Cold Brew Coffee", 380.0, 750.0, ["Credit Card", "UPI"]),
        ("DMart Hypermarket Monthly Provisions", 3500.0, 7800.0, ["Debit Card", "Credit Card"]),
        ("McDonalds Family Meal Deal", 520.0, 1100.0, ["UPI", "Credit Card"]),
        ("Chai Point Evening Tea & Snack", 120.0, 350.0, ["UPI"]),
        ("Domino's Pizza Weekend Feast", 680.0, 1450.0, ["Credit Card", "UPI"]),
    ],
    "Transportation": [
        ("Shell Petrol Station Fuel Auto Cut", 1500.0, 3500.0, ["Credit Card", "Debit Card"]),
        ("HPCL Smart Auto Fuel Top-up", 1200.0, 2800.0, ["Credit Card", "UPI"]),
        ("Uber Premier Trip to Office Tech Park", 280.0, 680.0, ["UPI", "Credit Card"]),
        ("Ola Cab Ride Airport Transit", 850.0, 1400.0, ["Credit Card", "UPI"]),
        ("Namma Metro Smart Card Recharge", 500.0, 1000.0, ["UPI", "Net Banking"]),
        ("FASTag Electronic Toll Plaza Debit", 180.0, 520.0, ["UPI", "Net Banking"]),
        ("Rapido Bike Taxi Commute", 65.0, 190.0, ["UPI"]),
    ],
    "Shopping": [
        ("Amazon India Electronics & Cable Purchase", 499.0, 4800.0, ["Credit Card", "Net Banking"]),
        ("Flipkart Big Billion Days Apparel", 1200.0, 5600.0, ["Credit Card", "UPI"]),
        ("Myntra Fashion Kurtas and Footwear", 1450.0, 4200.0, ["Credit Card", "UPI"]),
        ("Zara Lifestyle Clothing Store", 2800.0, 8900.0, ["Credit Card"]),
        ("Croma Digital Store Wireless Mouse", 699.0, 2400.0, ["Credit Card", "Debit Card"]),
        ("IKEA Home Organizers and Cushions", 1850.0, 6200.0, ["Credit Card"]),
        ("Decathlon Sports Gear & Shoes", 999.0, 3400.0, ["Credit Card", "UPI"]),
    ],
    "Utilities": [
        ("BESCOM Online Electricity Utility Bill", 1650.0, 3200.0, ["Net Banking", "UPI"]),
        ("Airtel Xstream Fiber Broadband Monthly", 1179.0, 1179.0, ["Credit Card", "Net Banking"]),
        ("Jio 5G Postpaid Family Mobile Bill", 799.0, 999.0, ["UPI", "Credit Card"]),
        ("Indane LPG Cooking Gas Cylinder", 950.0, 1050.0, ["UPI"]),
        ("BWSSB Municipal Water Bill Payment", 380.0, 720.0, ["Net Banking", "UPI"]),
    ],
    "Healthcare": [
        ("Apollo Pharmacy Prescription Medicines", 450.0, 2200.0, ["UPI", "Credit Card"]),
        ("Tata 1mg Diagnostic Complete Health Check", 1800.0, 3600.0, ["Credit Card", "Net Banking"]),
        ("Dr. Batra Clinic Dental Consultation", 800.0, 1500.0, ["UPI", "Credit Card"]),
        ("Max Healthcare Specialist OPD Fee", 1200.0, 2500.0, ["Credit Card"]),
        ("Pharmeasy Multivitamins and Supplements", 650.0, 1400.0, ["UPI"]),
    ],
    "Entertainment": [
        ("Netflix Premium 4K UHD Monthly Plan", 649.0, 649.0, ["Credit Card"]),
        ("Spotify Premium Individual Subscription", 119.0, 119.0, ["Credit Card", "UPI"]),
        ("Disney+ Hotstar Annual VIP Renewal", 1499.0, 1499.0, ["Credit Card", "UPI"]),
        ("PVR INOX IMAX 3D Weekend Movie Tickets", 950.0, 1850.0, ["Credit Card", "UPI"]),
        ("BookMyShow Standup Comedy Event Pass", 750.0, 2200.0, ["Credit Card", "UPI"]),
        ("Steam Online Gaming Digital Wallet Topup", 499.0, 2500.0, ["Credit Card"]),
    ],
    "Education": [
        ("Coursera Plus Annual Tech Specialization", 4999.0, 4999.0, ["Credit Card"]),
        ("Udemy Python Data Engineering Bootcamp", 499.0, 1299.0, ["Credit Card", "UPI"]),
        ("O'Reilly Media Technical Books & Library", 1250.0, 2500.0, ["Credit Card"]),
        ("Oracle Certified Professional Exam Voucher", 8500.0, 8500.0, ["Credit Card"]),
    ],
    "Travel": [
        ("IndiGo Airlines BLR to DEL Round Trip", 6500.0, 14500.0, ["Credit Card", "Net Banking"]),
        ("MakeMyTrip Heritage Hotel Resort Stay", 4500.0, 12000.0, ["Credit Card"]),
        ("IRCTC Tejas Express Executive Chair Car", 1450.0, 2800.0, ["Net Banking", "UPI"]),
        ("Uber Outstation Trip Booking", 2800.0, 5200.0, ["Credit Card", "UPI"]),
    ],
    "Other": [
        ("ATM Cash Withdrawal for Contingency", 2000.0, 5000.0, ["Debit Card"]),
        ("CRY Foundation Monthly Child Charity Gift", 500.0, 1000.0, ["Credit Card", "Net Banking"]),
        ("Society Festival Celebration Contribution", 750.0, 1500.0, ["UPI"]),
    ],
    "Uncategorised": [
        ("UNKNOWN VENDOR POS DEBIT 92841", 350.0, 1850.0, ["Debit Card", "Credit Card"]),
        ("MISC CHG BILLDESK TRF 81920", 120.0, 950.0, ["Net Banking"]),
        ("PAYU MERCHANT SETTLEMENT 4402", 480.0, 2100.0, ["Credit Card", "UPI"]),
        ("ACH DEBIT MANDATE UNVERIFIED 01", 650.0, 1450.0, ["Net Banking"]),
        ("RETAIL OUTLET 7719 TERMINAL B", 220.0, 880.0, ["Credit Card"]),
    ],
    "Refunds": [
        ("Amazon India Returned Goods Refund Reversal", 1299.0, 3499.0, ["Credit Card", "Net Banking"]),
        ("IndiGo Airlines Flight Cancellation Refund", 4800.0, 9500.0, ["Credit Card"]),
        ("Swiggy Missing Item Reimbursed Reversal", 240.0, 450.0, ["UPI"]),
        ("Flipkart Apparel Return Credit Reversal", 899.0, 1999.0, ["Credit Card", "UPI"]),
        ("Croma Double Charge Cashback Reversal", 699.0, 1500.0, ["Credit Card"]),
    ]
}


def generate_raw_dataset(output_path: str, count: int = 580) -> pd.DataFrame:
    """Generates the raw CSV dataset including realistic records and deliberate test anomalies."""
    rows = []
    
    # Generate spanning 3 calendar months: October 2026, November 2026, December 2026
    start_date = date(2026, 10, 1)
    end_date = date(2026, 12, 31)
    total_days = (end_date - start_date).days

    # 1. Ensure fixed recurring monthly income (1st of each month)
    for m, y in [(10, 2026), (11, 2026), (12, 2026)]:
        rows.append({
            "transaction_id": f"TXN-{y}{m:02d}-001",
            "transaction_date": date(y, m, 1).strftime("%Y-%m-%d"),
            "description": "HCL Technologies Monthly Payroll",
            "amount": 125000.0,
            "category": "Salary",
            "transaction_type": "INCOME",
            "payment_method": "Net Banking",
            "notes": "Direct payroll deposit"
        })
        rows.append({
            "transaction_id": f"TXN-{y}{m:02d}-002",
            "transaction_date": date(y, m, 15).strftime("%Y-%m-%d"),
            "description": "Freelance Python Architecture Consulting",
            "amount": 35000.0,
            "category": "Salary",
            "transaction_type": "INCOME",
            "payment_method": "Net Banking",
            "notes": "Consulting milestone fee"
        })

    # 2. Ensure fixed recurring housing rent (2nd of each month)
    for m, y in [(10, 2026), (11, 2026), (12, 2026)]:
        rows.append({
            "transaction_id": f"TXN-{y}{m:02d}-RENT",
            "transaction_date": date(y, m, 2).strftime("%Y-%m-%d"),
            "description": "Prestige Falcon City Apartment Rent",
            "amount": 22000.0,
            "category": "Housing",
            "transaction_type": "EXPENSE",
            "payment_method": "Net Banking",
            "notes": "Monthly residential rent"
        })

    # 3. Ensure Month-End Boundary transactions (28th, 29th, 30th, 31st)
    boundary_dates = [
        date(2026, 10, 28), date(2026, 10, 29), date(2026, 10, 30), date(2026, 10, 31),
        date(2026, 11, 28), date(2026, 11, 29), date(2026, 11, 30),
        date(2026, 12, 28), date(2026, 12, 29), date(2026, 12, 30), date(2026, 12, 31)
    ]
    for b_idx, b_date in enumerate(boundary_dates):
        rows.append({
            "transaction_id": f"TXN-BND-{b_idx+1:03d}",
            "transaction_date": b_date.strftime("%Y-%m-%d"),
            "description": "DMart Hypermarket Monthly Provisions",
            "amount": round(random.uniform(2500.0, 4800.0), 2),
            "category": "Food & Dining",
            "transaction_type": "EXPENSE",
            "payment_method": "Credit Card",
            "notes": f"Month-end grocery restock for {b_date.strftime('%B')}"
        })

    # 4. Generate legitimate refund entries (Test Case 2)
    for r_idx in range(12):
        desc, min_amt, max_amt, pms = random.choice(MERCHANT_CATALOG["Refunds"])
        rand_day = random.randint(0, total_days)
        t_date = start_date + timedelta(days=rand_day)
        rows.append({
            "transaction_id": f"TXN-REF-{r_idx+1:03d}",
            "transaction_date": t_date.strftime("%Y-%m-%d"),
            "description": desc,
            "amount": round(random.uniform(min_amt, max_amt), 2),
            "category": "Shopping" if "Amazon" in desc or "Flipkart" in desc or "Croma" in desc else "Travel" if "IndiGo" in desc else "Food & Dining",
            "transaction_type": "REFUND",
            "payment_method": random.choice(pms),
            "notes": "Verified merchant refund credit"
        })

    # 5. Generate Uncategorised entries (Test Case 1)
    for u_idx in range(18):
        desc, min_amt, max_amt, pms = random.choice(MERCHANT_CATALOG["Uncategorised"])
        rand_day = random.randint(0, total_days)
        t_date = start_date + timedelta(days=rand_day)
        rows.append({
            "transaction_id": f"TXN-UNC-{u_idx+1:03d}",
            "transaction_date": t_date.strftime("%Y-%m-%d"),
            "description": desc,
            "amount": round(random.uniform(min_amt, max_amt), 2),
            "category": "",  # Empty to test auto-classification fallback to 'Uncategorised'
            "transaction_type": "EXPENSE",
            "payment_method": random.choice(pms),
            "notes": "Unrecognized merchant gateway entry"
        })

    # 6. Fill remaining transactions across regular categories
    regular_categories = [
        "Food & Dining", "Transportation", "Shopping", "Education",
        "Healthcare", "Entertainment", "Utilities", "Travel", "Other"
    ]
    # Weightings to produce realistic spending distributions
    weights = [0.26, 0.18, 0.16, 0.06, 0.08, 0.10, 0.08, 0.05, 0.03]

    current_count = len(rows)
    target_count = count - 15  # leave room for deliberate test anomalies

    for i in range(current_count, target_count):
        cat = random.choices(regular_categories, weights=weights)[0]
        desc, min_a, max_a, pms = random.choice(MERCHANT_CATALOG[cat])
        rand_day = random.randint(0, total_days)
        t_date = start_date + timedelta(days=rand_day)
        amt = round(random.uniform(min_a, max_a), 2)
        pm = random.choice(pms)

        rows.append({
            "transaction_id": f"TXN-REG-{i+1:05d}",
            "transaction_date": t_date.strftime("%Y-%m-%d"),
            "description": desc,
            "amount": amt,
            "category": cat,
            "transaction_type": "EXPENSE",
            "payment_method": pm,
            "notes": "Regular transaction"
        })

    # 7. Deliberate Data Quality Test Anomalies (Exercising Test Cases 6 and 7)
    # A) Exact duplicate row
    dup_row = rows[10].copy()
    rows.append(dup_row)

    # B) Duplicate ID with different amount
    dup_id_row = rows[15].copy()
    dup_id_row["amount"] = 999.0
    rows.append(dup_id_row)

    # C) Missing date
    rows.append({
        "transaction_id": "TXN-ANOM-001",
        "transaction_date": "",
        "description": "Swiggy Order with Missing Date",
        "amount": 420.0,
        "category": "Food & Dining",
        "transaction_type": "EXPENSE",
        "payment_method": "UPI",
        "notes": "Data quality test: missing date"
    })

    # D) Non-positive / invalid amount
    rows.append({
        "transaction_id": "TXN-ANOM-002",
        "transaction_date": "2026-11-12",
        "description": "Starbucks with Negative Amount",
        "amount": -350.0,
        "category": "Food & Dining",
        "transaction_type": "EXPENSE",
        "payment_method": "Credit Card",
        "notes": "Data quality test: negative amount"
    })

    # E) Non-numeric amount string
    rows.append({
        "transaction_id": "TXN-ANOM-003",
        "transaction_date": "2026-11-14",
        "description": "Uber Ride with Corrupted Amount",
        "amount": "INVALID_AMT",
        "category": "Transportation",
        "transaction_type": "EXPENSE",
        "payment_method": "UPI",
        "notes": "Data quality test: text amount"
    })

    # F) Missing description
    rows.append({
        "transaction_id": "TXN-ANOM-004",
        "transaction_date": "2026-11-20",
        "description": "",
        "amount": 500.0,
        "category": "Other",
        "transaction_type": "EXPENSE",
        "payment_method": "Cash",
        "notes": "Data quality test: missing description"
    })

    raw_df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    raw_df.to_csv(output_path, index=False)
    print(f"Generated raw dataset: {len(raw_df)} records written to {output_path}")
    return raw_df


if __name__ == "__main__":
    raw_csv_path = os.path.join("data", "raw", "sample_expenses_raw.csv")
    generate_raw_dataset(raw_csv_path, count=620)
