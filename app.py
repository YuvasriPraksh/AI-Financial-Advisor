"""
app.py - AI Financial Advisor & Expense Manager
Main Streamlit application entry point.
Run with: streamlit run app.py
"""

import os
import io
from datetime import datetime

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from PIL import Image

# Local modules
from modules.database import (
    initialize_database,
    insert_expense,
    fetch_all_expenses,
    fetch_expenses_by_category,
    fetch_monthly_summary,
    get_summary_stats,
    delete_expense,
)
from modules.ocr import process_image
from modules.categorizer import categorize, get_all_categories
from modules.advisor import generate_financial_advice, generate_quick_tip
from modules.budget import calculate_budget, analyse_category_spending

# ──────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="AI Financial Advisor",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# CUSTOM CSS
# ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Dark gradient background */
.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    color: #e0e0e0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    border-right: 1px solid #0f3460;
}
[data-testid="stSidebar"] * { color: #e0e0e0 !important; }

/* Metric cards */
.metric-card {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    backdrop-filter: blur(10px);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.metric-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 32px rgba(100,100,255,0.2);
}
.metric-value {
    font-size: 1.9rem;
    font-weight: 700;
    color: #7c83fd;
}
.metric-label {
    font-size: 0.85rem;
    color: #a0a0b0;
    margin-top: 4px;
}

/* Section headers */
.section-header {
    font-size: 1.6rem;
    font-weight: 700;
    color: #ffffff;
    border-left: 4px solid #7c83fd;
    padding-left: 12px;
    margin-bottom: 20px;
}

/* Success/Info boxes */
.info-box {
    background: rgba(124,131,253,0.15);
    border: 1px solid rgba(124,131,253,0.4);
    border-radius: 12px;
    padding: 16px;
    margin: 10px 0;
}

/* Advice box */
.advice-box {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 16px;
    padding: 24px;
    line-height: 1.8;
    white-space: pre-wrap;
}

/* Table styling */
.stDataFrame { border-radius: 12px; overflow: hidden; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #7c83fd, #6c63ff);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 10px 24px;
    font-weight: 600;
    transition: all 0.2s ease;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #6c63ff, #5a52e0);
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(124,131,253,0.4);
}

/* Progress bar */
.stProgress > div > div { background: #7c83fd; }

/* Inputs */
.stTextInput > div > div, .stNumberInput > div > div, .stSelectbox > div > div {
    background: rgba(255,255,255,0.06) !important;
    border-color: rgba(255,255,255,0.2) !important;
    border-radius: 10px !important;
    color: #e0e0e0 !important;
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# INIT DB
# ──────────────────────────────────────────────
initialize_database()

# ──────────────────────────────────────────────
# SESSION STATE
# ──────────────────────────────────────────────
if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = ""
if "last_ocr_result" not in st.session_state:
    st.session_state.last_ocr_result = None

# ──────────────────────────────────────────────
# SIDEBAR NAVIGATION
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💰 AI Financial Advisor")
    st.markdown("---")

    page = st.radio(
        "Navigate",
        [
            "🏠 Home",
            "📸 Upload Screenshot",
            "📊 Expense Dashboard",
            "💼 Budget Planner",
            "🤖 AI Financial Advisor",
            "📈 Analytics",
            "🗄️ Manage Expenses",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("### 🔑 Gemini API Key")
    api_input = st.text_input(
        "Enter API Key",
        value=st.session_state.gemini_api_key,
        type="password",
        placeholder="AIza...",
        help="Get your free key at https://aistudio.google.com/",
    )
    if api_input:
        st.session_state.gemini_api_key = api_input
        st.success("API Key saved ✓")

    st.markdown("---")
    stats = get_summary_stats()
    st.markdown(f"**💳 Total Expenses:** ₹{stats['total_expenses']:,.2f}")
    st.markdown(f"**🔢 Transactions:** {stats['transaction_count']}")
    st.markdown(f"**🏆 Top Category:** {stats['highest_category']}")


# ══════════════════════════════════════════════
# PAGE: HOME
# ══════════════════════════════════════════════
if page == "🏠 Home":
    st.markdown('<div class="section-header">AI Financial Advisor & Expense Manager</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        <div class="info-box">
        <h3 style="color:#7c83fd; margin-top:0">Welcome! 👋</h3>
        <p>Your intelligent personal finance companion powered by <strong>Google Gemini AI</strong> and <strong>OCR technology</strong>. 
        Upload payment screenshots, track expenses, and receive personalised financial advice — all in one place.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 🚀 Key Features")
    features = [
        ("📸", "OCR Screenshot Processing", "Auto-extract amounts & merchants from PhonePe, GPay, Paytm"),
        ("🏷️", "Smart Categorization", "Instantly categorize Food, Transport, Shopping & 5 more"),
        ("📊", "Live Dashboard", "Real-time expense analytics with beautiful charts"),
        ("🤖", "Gemini AI Advice", "Personalised spending analysis and savings recommendations"),
        ("💼", "Budget Planner", "50/30/20 rule-based budget tracking with goal monitoring"),
        ("📈", "Analytics", "Monthly trends, pie charts, and bar graphs"),
    ]
    cols = st.columns(3)
    for i, (icon, title, desc) in enumerate(features):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="metric-card" style="margin-bottom:16px">
                <div style="font-size:2rem">{icon}</div>
                <div style="font-weight:600;color:#fff;margin:8px 0 4px">{title}</div>
                <div style="font-size:0.8rem;color:#a0a0b0">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("### ⚡ Quick Start")
    st.markdown("""
    1. **Add your Gemini API key** in the sidebar (free at [aistudio.google.com](https://aistudio.google.com/))
    2. **Upload a payment screenshot** → the AI extracts the amount and merchant automatically
    3. **Review your Dashboard** → see spending breakdowns and trends
    4. **Get AI Advice** → enter your income and savings goal for personalised recommendations
    """)

    if stats["transaction_count"] > 0:
        st.markdown("---")
        st.markdown("### 📌 Quick Stats")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="metric-card"><div class="metric-value">₹{stats["total_expenses"]:,.0f}</div><div class="metric-label">Total Spent</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{stats["transaction_count"]}</div><div class="metric-label">Transactions</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="metric-card"><div class="metric-value">₹{stats["average_spending"]:,.0f}</div><div class="metric-label">Avg per Transaction</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{stats["highest_category"]}</div><div class="metric-label">Top Category</div></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════
# PAGE: UPLOAD SCREENSHOT
# ══════════════════════════════════════════════
elif page == "📸 Upload Screenshot":
    st.markdown('<div class="section-header">📸 Upload Payment Screenshot</div>', unsafe_allow_html=True)

    col_upload, col_result = st.columns([1, 1])

    with col_upload:
        uploaded_file = st.file_uploader(
            "Upload a payment screenshot (PNG, JPG, JPEG)",
            type=["png", "jpg", "jpeg"],
            help="Supports PhonePe, Google Pay, Paytm, and general receipts",
        )

        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Screenshot", use_container_width=True)

            if st.button("🔍 Extract & Save Expense", use_container_width=True):
                with st.spinner("Running OCR..."):
                    result = process_image(image)
                    st.session_state.last_ocr_result = result

    with col_result:
        if st.session_state.last_ocr_result:
            result = st.session_state.last_ocr_result

            if "error" in result:
                st.error(f"OCR Error: {result['error']}")
            else:
                st.markdown("#### ✅ Extraction Results")

                confidence_color = {"HIGH": "🟢", "MEDIUM": "🟡", "LOW": "🔴"}.get(result["confidence"], "⚪")
                st.markdown(f"""
                <div class="info-box">
                    <p><strong>Confidence:</strong> {confidence_color} {result['confidence']}</p>
                    <p><strong>Merchant:</strong> {result['merchant']}</p>
                    <p><strong>Amount:</strong> ₹{result['amount']:,.2f}</p>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("#### ✏️ Review & Confirm")
                merchant_input = st.text_input("Merchant Name", value=result["merchant"])
                amount_input = st.number_input("Amount (₹)", value=float(result["amount"]), min_value=0.0, step=1.0)

                auto_cat = categorize(merchant_input, result.get("raw_text", ""))
                categories = get_all_categories()
                cat_idx = categories.index(auto_cat) if auto_cat in categories else 0
                category_input = st.selectbox("Category", categories, index=cat_idx)

                date_input = st.date_input("Date", value=datetime.today())

                if st.button("💾 Save Expense", use_container_width=True):
                    if amount_input <= 0:
                        st.error("Please enter a valid amount greater than 0.")
                    elif not merchant_input.strip():
                        st.error("Merchant name cannot be empty.")
                    else:
                        date_str = date_input.strftime("%Y-%m-%d %H:%M:%S")
                        insert_expense(merchant_input.strip(), amount_input, category_input, date_str)
                        st.success(f"✅ Saved: ₹{amount_input:,.2f} at {merchant_input} ({category_input})")
                        st.session_state.last_ocr_result = None
                        st.balloons()

                        # Quick AI tip
                        if st.session_state.gemini_api_key:
                            tip = generate_quick_tip(st.session_state.gemini_api_key, category_input, amount_input)
                            st.info(f"💡 **Quick Tip:** {tip}")

                with st.expander("📄 View Raw OCR Text"):
                    st.text(result.get("raw_text", "No text extracted."))

    # Manual entry section
    st.markdown("---")
    st.markdown("#### ➕ Or Add Expense Manually")
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        m_merchant = st.text_input("Merchant", placeholder="e.g. Swiggy", key="manual_merchant")
    with m2:
        m_amount = st.number_input("Amount (₹)", min_value=0.0, step=1.0, key="manual_amount")
    with m3:
        m_categories = get_all_categories()
        m_category = st.selectbox("Category", m_categories, key="manual_cat")
    with m4:
        m_date = st.date_input("Date", value=datetime.today(), key="manual_date")
    with m5:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Add", use_container_width=True, key="manual_add"):
            if m_amount <= 0:
                st.error("Amount must be > 0.")
            elif not m_merchant.strip():
                st.error("Merchant name required.")
            else:
                insert_expense(m_merchant.strip(), m_amount, m_category, m_date.strftime("%Y-%m-%d %H:%M:%S"))
                st.success(f"✅ Added ₹{m_amount:,.2f} for {m_merchant} ({m_category})")
                st.rerun()


# ══════════════════════════════════════════════
# PAGE: EXPENSE DASHBOARD
# ══════════════════════════════════════════════
elif page == "📊 Expense Dashboard":
    st.markdown('<div class="section-header">📊 Expense Dashboard</div>', unsafe_allow_html=True)

    stats = get_summary_stats()

    if stats["transaction_count"] == 0:
        st.info("📭 No expenses recorded yet. Upload a screenshot or add expenses manually.")
    else:
        # Summary metrics
        c1, c2, c3, c4, c5 = st.columns(5)
        metrics = [
            ("💳 Total Spent", f"₹{stats['total_expenses']:,.2f}"),
            ("🔢 Transactions", str(stats["transaction_count"])),
            ("🏆 Top Category", stats["highest_category"]),
            ("📊 Avg per Txn", f"₹{stats['average_spending']:,.2f}"),
            ("📅 Categories", str(len(stats["categories"]))),
        ]
        for col, (label, value) in zip([c1, c2, c3, c4, c5], metrics):
            with col:
                st.markdown(f'<div class="metric-card"><div class="metric-value">{value}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)

        st.markdown("---")

        # Category breakdown
        cat_df = fetch_expenses_by_category()
        if not cat_df.empty:
            st.markdown("### 🏷️ Category Breakdown")
            for _, row in cat_df.iterrows():
                pct = (row["total"] / stats["total_expenses"]) * 100
                col_a, col_b, col_c = st.columns([2, 5, 1])
                with col_a:
                    st.markdown(f"**{row['category']}**")
                with col_b:
                    st.progress(int(pct))
                with col_c:
                    st.markdown(f"₹{row['total']:,.2f}")

        # Recent transactions
        st.markdown("---")
        st.markdown("### 🕒 Recent Transactions")
        df = fetch_all_expenses()
        if not df.empty:
            display_df = df[["date", "merchant", "category", "amount"]].head(15).copy()
            display_df["amount"] = display_df["amount"].apply(lambda x: f"₹{x:,.2f}")
            display_df.columns = ["Date", "Merchant", "Category", "Amount"]
            st.dataframe(display_df, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════
# PAGE: BUDGET PLANNER
# ══════════════════════════════════════════════
elif page == "💼 Budget Planner":
    st.markdown('<div class="section-header">💼 Budget Planner</div>', unsafe_allow_html=True)

    col_input, col_output = st.columns([1, 2])

    with col_input:
        st.markdown("#### 💰 Your Financial Details")
        income = st.number_input("Monthly Income (₹)", min_value=0.0, step=1000.0, value=50000.0)
        savings_goal = st.number_input("Savings Goal / Month (₹)", min_value=0.0, step=500.0, value=10000.0)
        use_db = st.checkbox("Use expenses from database", value=True)
        if use_db:
            stats = get_summary_stats()
            total_exp = stats["total_expenses"]
            st.info(f"📊 Using ₹{total_exp:,.2f} total expenses from database.")
        else:
            total_exp = st.number_input("Custom Total Expenses (₹)", min_value=0.0, step=500.0)
        calculate_btn = st.button("📊 Calculate Budget", use_container_width=True)

    with col_output:
        if calculate_btn:
            if income <= 0:
                st.error("Monthly income must be greater than zero.")
            else:
                result = calculate_budget(income, total_exp, savings_goal)
                if "error" in result:
                    st.error(result["error"])
                else:
                    st.markdown(f"#### {result['budget_status']}")
                    st.markdown(f"*{result['status_detail']}*")

                    r1, r2, r3 = st.columns(3)
                    with r1:
                        st.markdown(f'<div class="metric-card"><div class="metric-value">₹{result["remaining_balance"]:,.0f}</div><div class="metric-label">Remaining Balance</div></div>', unsafe_allow_html=True)
                    with r2:
                        st.markdown(f'<div class="metric-card"><div class="metric-value">{result["savings_rate"]:.1f}%</div><div class="metric-label">Savings Rate</div></div>', unsafe_allow_html=True)
                    with r3:
                        st.markdown(f'<div class="metric-card"><div class="metric-value">{result["goal_achievement"]:.1f}%</div><div class="metric-label">Goal Achievement</div></div>', unsafe_allow_html=True)

                    st.markdown("---")
                    # Goal progress
                    st.markdown("#### 🎯 Savings Goal Progress")
                    progress_val = min(int(result["goal_achievement"]), 100)
                    st.progress(progress_val / 100)
                    if result["is_goal_met"]:
                        st.success(f"🎉 Goal of ₹{savings_goal:,.2f} is MET! You're saving ₹{result['remaining_balance']:,.2f}.")
                    else:
                        shortfall = savings_goal - result["remaining_balance"]
                        st.warning(f"⚠️ ₹{shortfall:,.2f} short of your savings goal.")

                    # 50/30/20 breakdown
                    st.markdown("#### 📐 50/30/20 Rule Breakdown")
                    rules = [
                        ("Needs (50%)", result["needs_budget"], "🏠"),
                        ("Wants (30%)", result["wants_budget"], "🎯"),
                        ("Savings (20%)", result["savings_budget"], "🏦"),
                    ]
                    rc1, rc2, rc3 = st.columns(3)
                    for col, (label, amount, icon) in zip([rc1, rc2, rc3], rules):
                        with col:
                            st.markdown(f'<div class="metric-card"><div style="font-size:1.5rem">{icon}</div><div class="metric-value">₹{amount:,.0f}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)

                    # Category analysis
                    if use_db:
                        cat_data = get_summary_stats()["categories"]
                        analysis = analyse_category_spending(cat_data, income)
                        if analysis:
                            st.markdown("---")
                            st.markdown("#### 📊 Category vs Budget")
                            cat_rows = []
                            for item in analysis:
                                cat_rows.append({
                                    "Category": item["category"],
                                    "Spent": f"₹{item['actual']:,.2f}",
                                    "Limit": f"₹{item['limit']:,.2f}",
                                    "Difference": f"₹{item['difference']:,.2f}",
                                    "Status": item["status"],
                                })
                            st.dataframe(pd.DataFrame(cat_rows), use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════
# PAGE: AI FINANCIAL ADVISOR
# ══════════════════════════════════════════════
elif page == "🤖 AI Financial Advisor":
    st.markdown('<div class="section-header">🤖 AI Financial Advisor</div>', unsafe_allow_html=True)

    if not st.session_state.gemini_api_key:
        st.warning("🔑 Please add your **Gemini API Key** in the sidebar to use the AI Advisor.")
        st.markdown("Get a free key at [aistudio.google.com](https://aistudio.google.com/app/apikey)")
    else:
        col_form, col_advice = st.columns([1, 2])

        with col_form:
            st.markdown("#### 📋 Your Financial Profile")
            ai_income = st.number_input("Monthly Income (₹)", min_value=0.0, step=1000.0, value=50000.0, key="ai_income")
            ai_goal = st.number_input("Monthly Savings Goal (₹)", min_value=0.0, step=500.0, value=10000.0, key="ai_goal")

            st.markdown("**📊 Expense Source**")
            use_live = st.checkbox("Use live database expenses", value=True, key="ai_live")

            if not use_live:
                st.markdown("*Enter custom expenses:*")
                custom_cats = get_all_categories()
                custom_expenses = {}
                for cat in custom_cats:
                    val = st.number_input(f"{cat} (₹)", min_value=0.0, step=100.0, key=f"ai_{cat}")
                    if val > 0:
                        custom_expenses[cat] = val

            generate_btn = st.button("🤖 Generate AI Advice", use_container_width=True)

        with col_advice:
            if generate_btn:
                if ai_income <= 0:
                    st.error("Income must be greater than zero.")
                else:
                    if use_live:
                        stats = get_summary_stats()
                        expenses_data = stats["categories"]
                        total = stats["total_expenses"]
                    else:
                        expenses_data = custom_expenses
                        total = sum(custom_expenses.values())

                    with st.spinner("🤖 Gemini AI is analysing your finances..."):
                        advice = generate_financial_advice(
                            api_key=st.session_state.gemini_api_key,
                            monthly_income=ai_income,
                            savings_goal=ai_goal,
                            expenses_by_category=expenses_data,
                            total_expenses=total,
                        )

                    st.markdown("#### 💡 Your Personalised Financial Report")
                    st.markdown(f'<div class="advice-box">{advice}</div>', unsafe_allow_html=True)

                    # Download button
                    st.download_button(
                        label="📥 Download Report",
                        data=advice,
                        file_name=f"financial_advice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain",
                    )


# ══════════════════════════════════════════════
# PAGE: ANALYTICS
# ══════════════════════════════════════════════
elif page == "📈 Analytics":
    st.markdown('<div class="section-header">📈 Analytics & Visualisations</div>', unsafe_allow_html=True)

    df = fetch_all_expenses()
    cat_df = fetch_expenses_by_category()
    monthly_df = fetch_monthly_summary()

    if df.empty:
        st.info("📭 No data yet. Add some expenses to see analytics.")
    else:
        # Chart colours
        COLORS = ["#7c83fd", "#6c63ff", "#ff6584", "#ffc75f", "#43e97b", "#38f9d7", "#fa709a", "#fee140"]

        tab1, tab2, tab3 = st.tabs(["🥧 Pie Chart", "📊 Bar Chart", "📅 Monthly Trend"])

        with tab1:
            st.markdown("### Category Distribution")
            if not cat_df.empty:
                fig, ax = plt.subplots(figsize=(8, 6))
                fig.patch.set_facecolor("#1a1a2e")
                ax.set_facecolor("#1a1a2e")
                wedges, texts, autotexts = ax.pie(
                    cat_df["total"],
                    labels=cat_df["category"],
                    autopct="%1.1f%%",
                    startangle=90,
                    colors=COLORS[: len(cat_df)],
                    pctdistance=0.8,
                )
                for text in texts:
                    text.set_color("#e0e0e0")
                for autotext in autotexts:
                    autotext.set_color("#ffffff")
                    autotext.set_fontsize(9)
                ax.set_title("Expense by Category", color="#ffffff", fontsize=14, fontweight="bold")
                st.pyplot(fig)
                plt.close(fig)

        with tab2:
            st.markdown("### Expense by Category (Bar Chart)")
            if not cat_df.empty:
                fig, ax = plt.subplots(figsize=(10, 5))
                fig.patch.set_facecolor("#1a1a2e")
                ax.set_facecolor("#1a1a2e")
                bars = ax.bar(
                    cat_df["category"],
                    cat_df["total"],
                    color=COLORS[: len(cat_df)],
                    edgecolor="none",
                    width=0.6,
                )
                ax.set_xlabel("Category", color="#e0e0e0")
                ax.set_ylabel("Amount (₹)", color="#e0e0e0")
                ax.set_title("Spending by Category", color="#ffffff", fontsize=14, fontweight="bold")
                ax.tick_params(colors="#e0e0e0")
                ax.spines[:].set_color("#333355")
                for bar in bars:
                    yval = bar.get_height()
                    ax.text(
                        bar.get_x() + bar.get_width() / 2,
                        yval + max(cat_df["total"]) * 0.01,
                        f"₹{yval:,.0f}",
                        ha="center",
                        va="bottom",
                        color="#e0e0e0",
                        fontsize=8,
                    )
                plt.xticks(rotation=30, ha="right")
                st.pyplot(fig)
                plt.close(fig)

        with tab3:
            st.markdown("### Monthly Expense Trend")
            if not monthly_df.empty:
                fig, ax = plt.subplots(figsize=(10, 5))
                fig.patch.set_facecolor("#1a1a2e")
                ax.set_facecolor("#1a1a2e")
                x = range(len(monthly_df))
                ax.fill_between(x, monthly_df["total"], alpha=0.3, color="#7c83fd")
                ax.plot(x, monthly_df["total"], color="#7c83fd", linewidth=2.5, marker="o", markersize=6)
                ax.set_xticks(x)
                ax.set_xticklabels(monthly_df["month"], rotation=30, ha="right", color="#e0e0e0")
                ax.set_ylabel("Amount (₹)", color="#e0e0e0")
                ax.set_title("Monthly Spending Trend", color="#ffffff", fontsize=14, fontweight="bold")
                ax.tick_params(colors="#e0e0e0")
                ax.spines[:].set_color("#333355")
                ax.grid(axis="y", color="#333355", linestyle="--", alpha=0.5)
                st.pyplot(fig)
                plt.close(fig)

                st.markdown("### 📅 Monthly Summary Table")
                monthly_display = monthly_df.copy()
                monthly_display["total"] = monthly_display["total"].apply(lambda x: f"₹{x:,.2f}")
                monthly_display.columns = ["Month", "Total Expenses", "Transactions"]
                st.dataframe(monthly_display, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════
# PAGE: MANAGE EXPENSES
# ══════════════════════════════════════════════
elif page == "🗄️ Manage Expenses":
    st.markdown('<div class="section-header">🗄️ Manage Expenses</div>', unsafe_allow_html=True)

    df = fetch_all_expenses()
    if df.empty:
        st.info("📭 No expenses found. Start by uploading a screenshot or adding an expense manually.")
    else:
        st.markdown(f"**Total records: {len(df)}**")

        # Filter
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            cats = ["All"] + get_all_categories()
            filter_cat = st.selectbox("Filter by Category", cats)
        with col_f2:
            search_query = st.text_input("Search Merchant", placeholder="e.g. Swiggy")

        filtered = df.copy()
        if filter_cat != "All":
            filtered = filtered[filtered["category"] == filter_cat]
        if search_query:
            filtered = filtered[filtered["merchant"].str.contains(search_query, case=False, na=False)]

        st.markdown(f"*Showing {len(filtered)} record(s)*")

        # Display with delete option
        for _, row in filtered.iterrows():
            col_d1, col_d2, col_d3, col_d4, col_d5 = st.columns([2, 2, 2, 1, 1])
            with col_d1:
                st.write(row["date"])
            with col_d2:
                st.write(row["merchant"])
            with col_d3:
                st.write(f"{row['category']} — ₹{row['amount']:,.2f}")
            with col_d4:
                st.write("")
            with col_d5:
                if st.button("🗑️", key=f"del_{row['id']}", help="Delete this expense"):
                    delete_expense(int(row["id"]))
                    st.success("Deleted.")
                    st.rerun()

        # Export
        st.markdown("---")
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="📥 Export All as CSV",
            data=csv_data,
            file_name=f"expenses_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )
