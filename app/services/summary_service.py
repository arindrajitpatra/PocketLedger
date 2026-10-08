from decimal import Decimal

from app.models import Transaction
from app.schemas import CategoryBreakdown, SummaryResponse
from app.services.currency_service import convert_currency


def calculate_monthly_summary(
    transactions: list[Transaction],
    month: str | None = None,
    currency: str = "INR"
) -> SummaryResponse:
    """
    Business service function to compute total income, total expenses,
    remaining balance, and category percentage breakdowns using Decimal arithmetic.
    Applies currency conversion to output values if display currency is requested.
    """
    total_income_inr = Decimal("0.00")
    total_expenses_inr = Decimal("0.00")

    expense_totals_inr: dict[str, Decimal] = {}
    income_totals_inr: dict[str, Decimal] = {}
    all_totals_inr: dict[str, Decimal] = {}

    for tx in transactions:
        amount = Decimal(str(tx.amount))
        all_totals_inr[tx.category] = all_totals_inr.get(tx.category, Decimal("0.00")) + amount

        if tx.type == "income":
            total_income_inr += amount
            income_totals_inr[tx.category] = income_totals_inr.get(tx.category, Decimal("0.00")) + amount
        elif tx.type == "expense":
            total_expenses_inr += amount
            expense_totals_inr[tx.category] = expense_totals_inr.get(tx.category, Decimal("0.00")) + amount

    remaining_balance_inr = total_income_inr - total_expenses_inr

    # Convert totals for display
    disp_income = convert_currency(total_income_inr, currency)
    disp_expenses = convert_currency(total_expenses_inr, currency)
    disp_balance = convert_currency(remaining_balance_inr, currency)

    # Expense category breakdown
    expense_breakdown: list[CategoryBreakdown] = []
    for cat, amt_inr in sorted(expense_totals_inr.items(), key=lambda x: x[1], reverse=True):
        pct = float(amt_inr / total_expenses_inr * Decimal("100.0")) if total_expenses_inr > 0 else 0.0
        disp_amt = convert_currency(amt_inr, currency)
        expense_breakdown.append(
            CategoryBreakdown(category=cat, amount=disp_amt, percentage=round(pct, 1))
        )

    # Income category breakdown
    income_breakdown: list[CategoryBreakdown] = []
    for cat, amt_inr in sorted(income_totals_inr.items(), key=lambda x: x[1], reverse=True):
        pct = float(amt_inr / total_income_inr * Decimal("100.0")) if total_income_inr > 0 else 0.0
        disp_amt = convert_currency(amt_inr, currency)
        income_breakdown.append(
            CategoryBreakdown(category=cat, amount=disp_amt, percentage=round(pct, 1))
        )

    # Combined breakdown
    total_all_inr = total_income_inr + total_expenses_inr
    all_breakdown: list[CategoryBreakdown] = []
    for cat, amt_inr in sorted(all_totals_inr.items(), key=lambda x: x[1], reverse=True):
        pct = float(amt_inr / total_all_inr * Decimal("100.0")) if total_all_inr > 0 else 0.0
        disp_amt = convert_currency(amt_inr, currency)
        all_breakdown.append(
            CategoryBreakdown(category=cat, amount=disp_amt, percentage=round(pct, 1))
        )

    return SummaryResponse(
        month=month,
        currency=currency.upper(),
        total_income=disp_income,
        total_expenses=disp_expenses,
        remaining_balance=disp_balance,
        category_breakdown=all_breakdown,
        expense_category_breakdown=expense_breakdown,
        income_category_breakdown=income_breakdown,
        transaction_count=len(transactions)
    )
