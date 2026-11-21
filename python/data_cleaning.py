"""
Data Cleaning & Preprocessing Pipeline
--------------------------------------
Implements professional ingestion, data hygiene, duplicate handling,
refund isolation, and comprehensive quality auditing. Never silently
discards transactions; all exclusions are tracked and explained.
"""

from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np
from datetime import datetime

from python.expense_categorization import (
    classify_transaction,
    STANDARD_CATEGORIES,
)


class DataQualityAudit:
    """Maintains a transparent record of all hygiene and cleaning operations."""

    def __init__(self):
        self.total_input_records: int = 0
        self.valid_records: int = 0
        self.invalid_records: int = 0
        self.missing_value_count: int = 0
        self.duplicate_count: int = 0
        self.uncategorised_count: int = 0
        self.refund_count: int = 0
        self.excluded_records: list = []
        self.cleaning_actions: list = []

    def log_exclusion(self, row_idx: Any, raw_data: dict, reason: str, severity: str = "ERROR"):
        self.invalid_records += 1
        self.excluded_records.append({
            "row_index": row_idx,
            "raw_record": raw_data,
            "reason": reason,
            "severity": severity,
            "timestamp": datetime.now().isoformat()
        })

    def log_action(self, action: str):
        self.cleaning_actions.append(action)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_input_records": self.total_input_records,
            "valid_records": self.valid_records,
            "invalid_records": self.invalid_records,
            "missing_value_count": self.missing_value_count,
            "duplicate_count": self.duplicate_count,
            "uncategorised_count": self.uncategorised_count,
            "refund_count": self.refund_count,
            "cleaning_actions": self.cleaning_actions,
            "quarantined_records_sample": self.excluded_records[:10]
        }


def clean_and_preprocess_transactions(
    raw_df: pd.DataFrame
) -> Tuple[pd.DataFrame, DataQualityAudit]:
    """
    Cleans, validates, and categorizes raw transaction records.
    
    Processing Steps:
    1. Standardize column headers.
    2. Audit input volume.
    3. Validate mandatory fields (date, amount, description).
    4. Detect and handle duplicates.
    5. Clean and parse dates.
    6. Validate numeric amounts.
    7. Execute automated categorization and refund classification.
    8. Compile detailed data quality report.
    """
    audit = DataQualityAudit()
    audit.total_input_records = len(raw_df)
    audit.log_action(f"Ingested {len(raw_df)} raw records from source CSV.")

    # 1. Standardize column names (strip whitespace, lowercase)
    df = raw_df.copy()
    df.columns = [str(col).strip().lower().replace(" ", "_") for col in df.columns]

    required_cols = {"transaction_date", "description", "amount"}
    missing_cols = required_cols - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing mandatory columns: {missing_cols}")

    valid_rows = []

    # 2. Row-by-row data hygiene and validation
    for idx, row in df.iterrows():
        raw_dict = row.to_dict()

        # Check missing date or description
        if pd.isna(row.get("transaction_date")) or str(row.get("transaction_date")).strip() in ("", "nan", "NaT"):
            audit.missing_value_count += 1
            audit.log_exclusion(idx, raw_dict, "Missing or null transaction_date")
            continue

        if pd.isna(row.get("description")) or str(row.get("description")).strip() in ("", "nan"):
            audit.missing_value_count += 1
            audit.log_exclusion(idx, raw_dict, "Missing or empty description")
            continue

        # Validate amount
        raw_amount = row.get("amount")
        try:
            amount_val = float(raw_amount)
            if np.isnan(amount_val):
                raise ValueError("Amount is NaN")
            if amount_val <= 0:
                audit.log_exclusion(idx, raw_dict, f"Invalid non-positive amount: {amount_val}")
                continue
        except (ValueError, TypeError):
            audit.log_exclusion(idx, raw_dict, f"Unparseable numeric amount: '{raw_amount}'")
            continue

        # Validate and parse date
        raw_date = str(row.get("transaction_date")).strip()
        parsed_date = None
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d", "%m/%d/%Y"):
            try:
                parsed_date = datetime.strptime(raw_date, fmt).date()
                break
            except ValueError:
                continue

        if not parsed_date:
            audit.log_exclusion(idx, raw_dict, f"Invalid date format: '{raw_date}'")
            continue

        # Extract payment method and notes safely
        payment_method = str(row.get("payment_method", "Other")).strip()
        if not payment_method or payment_method.lower() in ("nan", "none", ""):
            payment_method = "Other"

        notes = str(row.get("notes", "")).strip()
        if notes.lower() in ("nan", "none"):
            notes = ""

        raw_category = str(row.get("category", "")).strip()
        raw_type = str(row.get("transaction_type", "")).strip().upper()

        txn_id = str(row.get("transaction_id", f"TXN-{idx+10000}")).strip()

        # 3. Categorize and classify transaction
        category, txn_type = classify_transaction(
            description=str(row["description"]),
            raw_category=raw_category if raw_category else None,
            txn_type=raw_type if raw_type in ("INCOME", "EXPENSE", "REFUND") else None
        )

        valid_rows.append({
            "transaction_id": txn_id,
            "transaction_date": parsed_date,
            "description": str(row["description"]).strip(),
            "amount": round(amount_val, 2),
            "category": category,
            "transaction_type": txn_type,
            "payment_method": payment_method,
            "notes": notes,
            "year": parsed_date.year,
            "month": parsed_date.month,
            "day": parsed_date.day,
            "month_year": parsed_date.strftime("%Y-%m"),
            "raw_row_index": idx
        })

    cleaned_df = pd.DataFrame(valid_rows)
    audit.log_action(f"Completed initial data validation: {len(cleaned_df)} candidate records retained.")

    # 4. Duplicate Record Detection & Quarantine
    if not cleaned_df.empty:
        # Check explicit duplicate transaction_id
        dup_mask = cleaned_df.duplicated(subset=["transaction_id"], keep="first")
        if dup_mask.any():
            dup_records = cleaned_df[dup_mask]
            audit.duplicate_count += len(dup_records)
            for _, dup_row in dup_records.iterrows():
                audit.log_exclusion(
                    dup_row["raw_row_index"],
                    dup_row.to_dict(),
                    f"Duplicate transaction_id: {dup_row['transaction_id']}"
                )
            cleaned_df = cleaned_df[~dup_mask].copy()
            audit.log_action(f"Quarantined {len(dup_records)} records with duplicate transaction IDs.")

        # Check duplicate business identity (same date, description, amount, payment_method)
        dup_biz_mask = cleaned_df.duplicated(
            subset=["transaction_date", "description", "amount", "payment_method"],
            keep="first"
        )
        if dup_biz_mask.any():
            dup_biz = cleaned_df[dup_biz_mask]
            audit.duplicate_count += len(dup_biz)
            for _, dup_row in dup_biz.iterrows():
                audit.log_exclusion(
                    dup_row["raw_row_index"],
                    dup_row.to_dict(),
                    "Duplicate business entry (identical date, description, amount, payment method)"
                )
            cleaned_df = cleaned_df[~dup_biz_mask].copy()
            audit.log_action(f"Quarantined {len(dup_biz)} identical duplicate transaction rows.")

    # 5. Calculate Metrics for Audit
    if not cleaned_df.empty:
        audit.valid_records = len(cleaned_df)
        audit.uncategorised_count = int((cleaned_df["category"] == "Uncategorised").sum())
        audit.refund_count = int((cleaned_df["transaction_type"] == "REFUND").sum())

    audit.log_action(
        f"Pipeline complete. Valid: {audit.valid_records}, Excluded: {audit.invalid_records}, "
        f"Duplicates: {audit.duplicate_count}, Uncategorised: {audit.uncategorised_count}, "
        f"Refunds: {audit.refund_count}."
    )

    # Sort deterministically by date and transaction_id
    cleaned_df = cleaned_df.sort_values(by=["transaction_date", "transaction_id"]).reset_index(drop=True)
    return cleaned_df, audit
