"""
budget.py - Budget Planning and Financial Calculations
Computes budget metrics and goal achievement.
"""


def calculate_budget(monthly_income: float, total_expenses: float, savings_goal: float) -> dict:
    """
    Compute comprehensive budget metrics using the 50/30/20 rule.

    Args:
        monthly_income:  Gross monthly income (INR).
        total_expenses:  Total expenses for the period (INR).
        savings_goal:    Target monthly savings (INR).

    Returns:
        dict: Budget metrics ready for display.
    """
    if monthly_income <= 0:
        return {
            "error": "Monthly income must be greater than zero.",
        }

    remaining_balance = monthly_income - total_expenses
    savings_rate = (remaining_balance / monthly_income) * 100
    expense_rate = (total_expenses / monthly_income) * 100

    # Goal achievement
    goal_achievement = 0.0
    if savings_goal > 0:
        goal_achievement = min((remaining_balance / savings_goal) * 100, 100.0)
    is_goal_met = remaining_balance >= savings_goal

    # 50/30/20 rule benchmarks
    needs_budget = monthly_income * 0.50
    wants_budget = monthly_income * 0.30
    savings_budget = monthly_income * 0.20

    # Budget status
    if expense_rate <= 50:
        budget_status = "🟢 Excellent"
        status_detail = "You are well within budget. Great discipline!"
    elif expense_rate <= 70:
        budget_status = "🟡 Good"
        status_detail = "Spending is moderate. Small tweaks can help you save more."
    elif expense_rate <= 90:
        budget_status = "🟠 Warning"
        status_detail = "High expense ratio. Review discretionary spending."
    else:
        budget_status = "🔴 Critical"
        status_detail = "Expenses exceed safe limits. Immediate budget review needed."

    return {
        "monthly_income": monthly_income,
        "total_expenses": total_expenses,
        "remaining_balance": remaining_balance,
        "savings_rate": round(savings_rate, 2),
        "expense_rate": round(expense_rate, 2),
        "savings_goal": savings_goal,
        "goal_achievement": round(goal_achievement, 2),
        "is_goal_met": is_goal_met,
        "needs_budget": needs_budget,
        "wants_budget": wants_budget,
        "savings_budget": savings_budget,
        "budget_status": budget_status,
        "status_detail": status_detail,
    }


def get_category_budget_limits(monthly_income: float) -> dict:
    """
    Return recommended budget limits per category based on income.
    Uses a practical allocation model for Indian households.
    """
    return {
        "Food":          round(monthly_income * 0.15, 2),
        "Transport":     round(monthly_income * 0.10, 2),
        "Shopping":      round(monthly_income * 0.10, 2),
        "Entertainment": round(monthly_income * 0.05, 2),
        "Bills":         round(monthly_income * 0.15, 2),
        "Healthcare":    round(monthly_income * 0.05, 2),
        "Education":     round(monthly_income * 0.10, 2),
        "Others":        round(monthly_income * 0.05, 2),
    }


def analyse_category_spending(
    expenses_by_category: dict, monthly_income: float
) -> list:
    """
    Compare actual spending vs recommended limits per category.

    Returns a list of dicts:
      {category, actual, limit, difference, status}
    """
    limits = get_category_budget_limits(monthly_income)
    results = []
    for category, limit in limits.items():
        actual = expenses_by_category.get(category, 0.0)
        diff = limit - actual
        if actual == 0:
            status = "💤 No Spend"
        elif actual <= limit * 0.75:
            status = "🟢 Under Budget"
        elif actual <= limit:
            status = "🟡 Near Limit"
        else:
            status = "🔴 Over Budget"
        results.append({
            "category": category,
            "actual": actual,
            "limit": limit,
            "difference": round(diff, 2),
            "status": status,
        })
    return results
