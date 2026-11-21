"""
Database Schema Diagram Generator using Pillow
----------------------------------------------
Generates a crisp, high-resolution PNG diagram of the normalized Oracle 3NF schema
and Power BI Star Schema using PIL (Pillow).
"""

import os
from PIL import Image, ImageDraw, ImageFont


def generate_schema_diagram(output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    width, height = 1600, 1100
    img = Image.new("RGB", (width, height), color="#0f172a")
    draw = ImageDraw.Draw(img)

    # Use default font or load standard truetype if available
    font_title = ImageFont.load_default()
    font_sub = ImageFont.load_default()
    font_hdr = ImageFont.load_default()
    font_txt = ImageFont.load_default()

    # Try loading Arial / Segoe UI on Windows for ultra-crisp typography
    try:
        font_title = ImageFont.truetype("arialbd.ttf", 32)
        font_sub = ImageFont.truetype("arial.ttf", 18)
        font_hdr = ImageFont.truetype("segoeuib.ttf", 16)
        font_txt = ImageFont.truetype("consola.ttf", 13)
        font_sm = ImageFont.truetype("arial.ttf", 12)
    except Exception:
        pass

    # Header Title
    draw.text((width // 2, 45), "PERSONAL EXPENSE TRACKER & BUDGET DASHBOARD", fill="#38bdf8", font=font_title, anchor="mm")
    draw.text((width // 2, 85), "Enterprise Relational Schema (Oracle 3NF) & Power BI Star-Schema Model", fill="#94a3b8", font=font_sub, anchor="mm")

    def draw_card(x, y, w, h, title, cols, hdr_color="#0284c7", border_color="#38bdf8"):
        # Card Body
        draw.rounded_rectangle([x, y, x + w, y + h], radius=10, fill="#1e293b", outline=border_color, width=2)
        # Card Header
        draw.rounded_rectangle([x, y, x + w, y + 42], radius=10, fill=hdr_color, outline=border_color, width=2)
        # Fill square bottom corners of header
        draw.rectangle([x, y + 20, x + w, y + 42], fill=hdr_color)
        draw.text((x + w // 2, y + 21), title, fill="#ffffff", font=font_hdr, anchor="mm")

        # Column list
        cur_y = y + 54
        for col in cols:
            if "PK" in col:
                text_col = "#fbbf24"
            elif "FK" in col:
                text_col = "#34d399"
            else:
                text_col = "#cbd5e1"
            draw.text((x + 18, cur_y), col, fill=text_col, font=font_txt)
            cur_y += 24

    # 1. TRANSACTIONS FACT (Center)
    txn_cols = [
        "TRANSACTION_ID (PK)    NUMBER(10)",
        "TRANSACTION_DATE (IDX) DATE",
        "DESCRIPTION            VARCHAR2(255)",
        "AMOUNT                 NUMBER(12,2)",
        "CATEGORY_ID (FK, IDX)  NUMBER(5)",
        "TRANSACTION_TYPE (IDX) VARCHAR2(10)",
        "PAYMENT_METHOD         VARCHAR2(30)",
        "NOTES                  VARCHAR2(500)",
        "SOURCE_RAW_ID          VARCHAR2(50)",
        "CREATED_AT             TIMESTAMP"
    ]
    draw_card(600, 360, 400, 320, "FACT: TRANSACTIONS", txn_cols, hdr_color="#0284c7", border_color="#38bdf8")

    # 2. CATEGORIES (Dimension - Left Top)
    cat_cols = [
        "CATEGORY_ID (PK)   NUMBER(5)",
        "CATEGORY_NAME (UQ) VARCHAR2(50)",
        "CATEGORY_TYPE      VARCHAR2(20)",
        "DESCRIPTION        VARCHAR2(255)",
        "IS_ACTIVE          CHAR(1)",
        "CREATED_AT         TIMESTAMP"
    ]
    draw_card(100, 240, 380, 220, "DIM: CATEGORIES", cat_cols, hdr_color="#047857", border_color="#34d399")

    # 3. PAYMENT_METHODS (Dimension - Left Bottom)
    pm_cols = [
        "PAYMENT_METHOD_ID (PK) NUMBER(3)",
        "METHOD_NAME (UQ)       VARCHAR2(30)",
        "CHANNEL_TYPE           VARCHAR2(20)",
        "IS_ACTIVE              CHAR(1)"
    ]
    draw_card(100, 620, 380, 180, "DIM: PAYMENT_METHODS", pm_cols, hdr_color="#4d7c0f", border_color="#a3e635")

    # 4. MONTHLY_BUDGET (Dimension/Fact - Right Top)
    budget_cols = [
        "BUDGET_ID (PK)      NUMBER(10)",
        "CATEGORY_ID (FK)    NUMBER(5)",
        "BUDGET_MONTH (IDX)  NUMBER(2)",
        "BUDGET_YEAR (IDX)   NUMBER(4)",
        "BUDGET_AMOUNT       NUMBER(12,2)",
        "UQ (CAT_ID, MONTH, YEAR)",
        "CREATED_AT          TIMESTAMP"
    ]
    draw_card(1120, 240, 380, 240, "FACT/DIM: MONTHLY_BUDGET", budget_cols, hdr_color="#b45309", border_color="#fbbf24")

    # 5. BUDGET_BREACH_LOG (Audit/Log - Right Bottom)
    breach_cols = [
        "LOG_ID (PK)         NUMBER(10)",
        "CATEGORY_ID (FK)    NUMBER(5)",
        "LOG_MONTH           NUMBER(2)",
        "LOG_YEAR            NUMBER(4)",
        "BUDGET_AMOUNT       NUMBER(12,2)",
        "ACTUAL_SPEND        NUMBER(12,2)",
        "VARIANCE_AMOUNT     NUMBER(12,2)",
        "BREACH_STATUS       VARCHAR2(20)",
        "DETECTED_AT         TIMESTAMP"
    ]
    draw_card(1120, 580, 380, 280, "LOG: BUDGET_BREACH_LOG", breach_cols, hdr_color="#be123c", border_color="#f43f5e")

    # 6. DIM_DATE (Power BI Star Schema Dimension - Top Middle)
    date_cols = [
        "DATE_KEY (PK)  DATE [YYYY-MM-DD]",
        "CALENDAR_YEAR  NUMBER(4)",
        "MONTH_NAME     VARCHAR2(15)",
        "MONTH_YEAR     VARCHAR2(10)",
        "IS_MONTH_END   CHAR(1)"
    ]
    draw_card(600, 140, 400, 180, "DIM: DIM_DATE (STAR SCHEMA)", date_cols, hdr_color="#4338ca", border_color="#818cf8")

    # Connectors & Arrows
    # Categories -> Transactions
    draw.line([(480, 350), (600, 480)], fill="#34d399", width=3)
    draw.polygon([(590, 470), (600, 480), (595, 490)], fill="#34d399")
    draw.text((505, 400), "1 : N (FK)", fill="#34d399", font=font_sm)

    # Categories -> Monthly Budget
    draw.line([(480, 310), (1120, 310)], fill="#34d399", width=2)
    draw.text((760, 290), "1 : N (Budgets)", fill="#34d399", font=font_sm)

    # Payment Methods -> Transactions
    draw.line([(480, 710), (600, 580)], fill="#a3e635", width=3)
    draw.polygon([(590, 585), (600, 580), (598, 595)], fill="#a3e635")
    draw.text((515, 660), "1 : N (PM)", fill="#a3e635", font=font_sm)

    # Dim Date -> Transactions
    draw.line([(800, 320), (800, 360)], fill="#818cf8", width=3)
    draw.polygon([(795, 350), (800, 360), (805, 350)], fill="#818cf8")
    draw.text((810, 335), "1 : N", fill="#818cf8", font=font_sm)

    # Transactions -> Budget Breach Log (Evaluation trigger/PLSQL)
    draw.line([(1000, 520), (1120, 680)], fill="#f43f5e", width=2)
    draw.text((1010, 580), "PL/SQL Breach Check", fill="#f43f5e", font=font_sm)

    # Legend / Footer
    draw.text((width // 2, 980), "Normalized Form: 3NF | Star-Schema Optimized for Power BI & Oracle Analytical Views",
              fill="#64748b", font=font_sub, anchor="mm")
    draw.text((width // 2, 1015), "Primary Keys (Gold) | Foreign Keys (Emerald) | Ledger Attributes (Silver)",
              fill="#94a3b8", font=font_sm, anchor="mm")

    img.save(output_path, "PNG", quality=95)
    print(f"Schema diagram created: {output_path}")


if __name__ == "__main__":
    out_file = os.path.join("diagrams", "database_schema.png")
    generate_schema_diagram(out_file)
