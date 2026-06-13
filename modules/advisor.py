"""
advisor.py - AI Financial Advisor using Google Gemini API
Generates personalised financial advice based on expense data.
"""

import os
import google.generativeai as genai


def _init_gemini(api_key: str):
    """Configure and return the Gemini generative model."""
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-1.5-flash")


def generate_financial_advice(
    api_key: str,
    monthly_income: float,
    savings_goal: float,
    expenses_by_category: dict,
    total_expenses: float,
) -> str:
    """
    Generate comprehensive financial advice using Gemini AI.

    Args:
        api_key:               Google Gemini API key.
        monthly_income:        User's monthly income (INR).
        savings_goal:          Desired monthly savings (INR).
        expenses_by_category:  Dict of {category: amount}.
        total_expenses:        Total expenses this month (INR).

    Returns:
        str: Formatted financial advice from Gemini.
    """
    if not api_key or api_key.strip() == "":
        return "❌ Please enter a valid Gemini API key to get AI advice."

    try:
        model = _init_gemini(api_key.strip())

        remaining = monthly_income - total_expenses
        savings_rate = (remaining / monthly_income * 100) if monthly_income > 0 else 0

        # Build a readable expense breakdown
        expense_breakdown = "\n".join(
            f"  • {cat}: ₹{amt:,.2f}" for cat, amt in expenses_by_category.items()
        ) or "  • No expenses recorded yet."

        prompt = f"""
You are a certified financial advisor for Indian users. Analyse the following financial data and provide detailed, actionable, and personalised advice.

---
FINANCIAL SNAPSHOT
---
Monthly Income     : ₹{monthly_income:,.2f}
Total Expenses     : ₹{total_expenses:,.2f}
Remaining Balance  : ₹{remaining:,.2f}
Current Savings Rate: {savings_rate:.1f}%
Savings Goal       : ₹{savings_goal:,.2f}/month

EXPENSE BREAKDOWN BY CATEGORY:
{expense_breakdown}
---

Please provide a comprehensive financial report with the following sections. Use emojis for readability:

1. 📊 SPENDING ANALYSIS
   - Comment on each major spending category.
   - Highlight overspending areas compared to standard benchmarks (50/30/20 rule).

2. 💰 BUDGET RECOMMENDATIONS
   - Suggest an ideal monthly budget for each category based on income.
   - Use the 50/30/20 rule as a baseline (needs/wants/savings).

3. 🏦 SAVINGS SUGGESTIONS
   - Actionable steps to reach the savings goal of ₹{savings_goal:,.2f}.
   - Recommend suitable savings instruments (FD, RD, SIP, PPF, etc.) for an Indian user.

4. ✂️ EXPENSE REDUCTION TIPS
   - Specific tips to reduce spending in the top 3 expense categories.
   - Suggest app/service alternatives or lifestyle changes.

5. 🩺 FINANCIAL HEALTH SUMMARY
   - Rate the overall financial health: Excellent / Good / Fair / Needs Improvement.
   - Provide a concise 3-sentence summary of the user's financial situation.
   - Give a motivational closing statement.

Keep the tone professional yet friendly. Use Indian Rupee (₹) throughout.
"""

        response = model.generate_content(prompt)
        return response.text

    except Exception as exc:
        error_msg = str(exc)
        if "API_KEY_INVALID" in error_msg or "API key" in error_msg:
            return "❌ Invalid API Key. Please check your Gemini API key and try again."
        elif "quota" in error_msg.lower():
            return "❌ API quota exceeded. Please check your Gemini API usage limits."
        else:
            return f"❌ Error generating advice: {error_msg}"


def generate_quick_tip(api_key: str, category: str, amount: float) -> str:
    """
    Generate a single quick tip for a specific expense.

    Args:
        api_key:  Google Gemini API key.
        category: Expense category.
        amount:   Amount spent.

    Returns:
        str: A brief financial tip.
    """
    if not api_key or api_key.strip() == "":
        return "Enter your API key to get personalised tips."

    try:
        model = _init_gemini(api_key.strip())
        prompt = (
            f"You just spent ₹{amount:,.2f} on {category}. "
            "Give one short, practical money-saving tip in 2 sentences for an Indian user."
        )
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception:
        return "💡 Track your spending consistently to build better financial habits."
