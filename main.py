import csv
from datetime import datetime
from enum import Enum
from functools import wraps
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class Category(Enum):
    INCOME = "Income"
    EXPENSE = "Expense"


# Color constants
COLORS = {
    Category.INCOME.value: "#2ecc71",
    Category.EXPENSE.value: "#e74c3c",
    "savings": "#3498db",
}

DATE_FORMAT = "%d-%m-%Y"


def requires_data(func):
    """Decorator to check if DataFrame is empty before visualization."""
    @wraps(func)
    def wrapper(df, *args, **kwargs):
        if df.empty:
            print("No data to visualize.")
            return
        return func(df, *args, **kwargs)
    return wrapper


class TransactionStore:
    """Handles CSV storage and retrieval of financial transactions."""

    def __init__(self, filepath="finance_data.csv"):
        self.filepath = Path(filepath)
        self.columns = ["date", "amount", "category", "description"]

    def initialize(self):
        if not self.filepath.exists() or self.filepath.stat().st_size == 0:
            df = pd.DataFrame(columns=self.columns)
            df.to_csv(self.filepath, index=False)
            print(f"Initialized {self.filepath}")

    def add_entry(self, date, amount, category, description):
        new_entry = {
            "date": date,
            "amount": amount,
            "category": category,
            "description": description,
        }
        with open(self.filepath, "a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.columns)
            writer.writerow(new_entry)
        print("Entry added successfully")

    def get_transactions_df(self, start_date=None, end_date=None):
        """Returns a DataFrame of transactions, optionally filtered by date range."""
        self.initialize()
        df = pd.read_csv(self.filepath)

        if df.empty:
            return df

        df["date"] = pd.to_datetime(df["date"], format=DATE_FORMAT, errors="coerce")
        df = df.dropna(subset=["date"])

        if start_date and end_date:
            start = datetime.strptime(start_date, DATE_FORMAT)
            end = datetime.strptime(end_date, DATE_FORMAT)
            mask = (df["date"] >= start) & (df["date"] <= end)
            df = df.loc[mask]

        return df.sort_values("date")

    def get_transactions(self, start_date, end_date):
        df = self.get_transactions_df(start_date, end_date)

        if df.empty:
            print("No transactions found in the given date range.")
            return df

        print(f"\nTransactions from {start_date} to {end_date}")
        print(df.to_string(index=False, formatters={"date": lambda x: x.strftime(DATE_FORMAT)}))

        total_income = df[df["category"] == Category.INCOME.value]["amount"].sum()
        total_expense = df[df["category"] == Category.EXPENSE.value]["amount"].sum()
        print("\nSummary:")
        print(f"Total income: ${total_income:.2f}")
        print(f"Total expense: ${total_expense:.2f}")
        print(f"Net savings: ${(total_income - total_expense):.2f}")

        return df


class Visualizer:
    """Handles all Plotly visualizations for financial data."""

    @staticmethod
    @requires_data
    def income_vs_expense_bar(df):
        """Bar chart comparing total income vs expense."""
        summary = df.groupby("category")["amount"].sum().reset_index()

        fig = px.bar(
            summary,
            x="category",
            y="amount",
            color="category",
            color_discrete_map=COLORS,
            title="Income vs Expense",
            labels={"amount": "Amount ($)", "category": "Category"},
        )
        fig.update_layout(showlegend=False)
        fig.show()

    @staticmethod
    @requires_data
    def spending_over_time(df):
        """Line chart showing income and expenses over time."""
        daily = df.groupby(["date", "category"])["amount"].sum().reset_index()

        fig = px.line(
            daily,
            x="date",
            y="amount",
            color="category",
            color_discrete_map=COLORS,
            title="Transactions Over Time",
            labels={"amount": "Amount ($)", "date": "Date"},
            markers=True,
        )
        fig.show()

    @staticmethod
    @requires_data
    def monthly_summary(df):
        """Bar chart showing monthly income vs expense."""
        df = df.copy()
        df["month"] = df["date"].dt.to_period("M").astype(str)

        monthly = df.groupby(["month", "category"])["amount"].sum().reset_index()

        fig = px.bar(
            monthly,
            x="month",
            y="amount",
            color="category",
            barmode="group",
            color_discrete_map=COLORS,
            title="Monthly Income vs Expense",
            labels={"amount": "Amount ($)", "month": "Month"},
        )
        fig.show()

    @staticmethod
    @requires_data
    def category_pie_chart(df, category=Category.EXPENSE.value):
        """Pie chart showing breakdown by description for a category."""
        filtered = df[df["category"] == category]
        if filtered.empty:
            print(f"No {category.lower()} data to visualize.")
            return

        by_desc = filtered.groupby("description")["amount"].sum().reset_index()

        fig = px.pie(
            by_desc,
            values="amount",
            names="description",
            title=f"{category} Breakdown by Description",
            hole=0.4,
        )
        fig.show()

    @staticmethod
    @requires_data
    def cumulative_savings(df):
        """Line chart showing cumulative savings over time."""
        df = df.copy().sort_values("date")
        df["signed_amount"] = df["amount"].where(
            df["category"] == Category.INCOME.value, -df["amount"]
        )
        df["cumulative"] = df["signed_amount"].cumsum()

        fig = px.area(
            df,
            x="date",
            y="cumulative",
            title="Cumulative Savings Over Time",
            labels={"cumulative": "Savings ($)", "date": "Date"},
        )
        fig.update_traces(
            line_color=COLORS["savings"],
            fillcolor="rgba(52, 152, 219, 0.3)",
        )
        fig.show()

    @staticmethod
    @requires_data
    def dashboard(df):
        """Full dashboard with multiple charts."""
        df = df.copy()
        df["month"] = df["date"].dt.to_period("M").astype(str)
        df["signed_amount"] = df["amount"].where(
            df["category"] == Category.INCOME.value, -df["amount"]
        )
        df["cumulative"] = df.sort_values("date")["signed_amount"].cumsum()

        total_income = df[df["category"] == Category.INCOME.value]["amount"].sum()
        total_expense = df[df["category"] == Category.EXPENSE.value]["amount"].sum()
        net_savings = total_income - total_expense

        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=(
                "Income vs Expense",
                "Cumulative Savings",
                "Monthly Breakdown",
                "Expense by Description",
            ),
            specs=[
                [{"type": "bar"}, {"type": "scatter"}],
                [{"type": "bar"}, {"type": "pie"}],
            ],
        )

        # Income vs Expense bar
        summary = df.groupby("category")["amount"].sum().reset_index()
        colors = [COLORS.get(c, "#999999") for c in summary["category"]]
        fig.add_trace(
            go.Bar(
                x=summary["category"],
                y=summary["amount"],
                marker_color=colors,
                name="Total",
            ),
            row=1,
            col=1,
        )

        # Cumulative savings line
        sorted_df = df.sort_values("date")
        fig.add_trace(
            go.Scatter(
                x=sorted_df["date"],
                y=sorted_df["cumulative"],
                mode="lines+markers",
                name="Savings",
                line={"color": COLORS["savings"]},
                fill="tozeroy",
            ),
            row=1,
            col=2,
        )

        # Monthly breakdown
        monthly = df.groupby(["month", "category"])["amount"].sum().reset_index()
        for cat in Category:
            cat_data = monthly[monthly["category"] == cat.value]
            fig.add_trace(
                go.Bar(
                    x=cat_data["month"],
                    y=cat_data["amount"],
                    name=cat.value,
                    marker_color=COLORS[cat.value],
                ),
                row=2,
                col=1,
            )

        # Expense pie chart
        expenses = df[df["category"] == Category.EXPENSE.value]
        if not expenses.empty:
            by_desc = expenses.groupby("description")["amount"].sum().reset_index()
            fig.add_trace(
                go.Pie(
                    labels=by_desc["description"],
                    values=by_desc["amount"],
                    hole=0.4,
                ),
                row=2,
                col=2,
            )

        fig.update_layout(
            height=800,
            title_text=(
                f"Financial Dashboard | Income: ${total_income:,.2f} | "
                f"Expense: ${total_expense:,.2f} | Net: ${net_savings:,.2f}"
            ),
            showlegend=True,
        )
        fig.show()


# Data entry functions
def get_date(prompt, allow_default=False):
    while True:
        date_str = input(f"{prompt}: ").strip()
        if allow_default and date_str == "":
            today = datetime.today().strftime(DATE_FORMAT)
            print(f"Using today's date: {today}")
            return today
        try:
            parsed = datetime.strptime(date_str, DATE_FORMAT)
            return parsed.strftime(DATE_FORMAT)
        except ValueError:
            print("Invalid date format. Please use dd-mm-yyyy (e.g., 19-12-2025)")


def get_amount():
    while True:
        try:
            amount = float(input("Enter the amount: "))
            if amount <= 0:
                raise ValueError("Amount must be positive.")
            return amount
        except ValueError as e:
            print(e)


def get_category():
    while True:
        choice = input("Enter the category ('I' for Income or 'E' for Expense): ").upper()
        if choice == "I":
            return Category.INCOME.value
        if choice == "E":
            return Category.EXPENSE.value
        print("Invalid category. Please enter 'I' or 'E'.")


def get_description():
    return input("Enter a description (optional): ").strip()


def add(store):
    store.initialize()
    date = get_date("Enter the date (dd-mm-yyyy) or press Enter for today", allow_default=True)
    amount = get_amount()
    category = get_category()
    description = get_description()
    store.add_entry(date, amount, category, description)


def visualize_menu(store):
    """Sub-menu for visualization options."""
    start_date = get_date("Enter start date (dd-mm-yyyy)")
    end_date = get_date("Enter end date (dd-mm-yyyy)")
    df = store.get_transactions_df(start_date, end_date)

    if df.empty:
        print("No data to visualize for this date range.")
        return

    menu_options = {
        "1": ("Income vs Expense (Bar)", lambda: Visualizer.income_vs_expense_bar(df)),
        "2": ("Transactions Over Time (Line)", lambda: Visualizer.spending_over_time(df)),
        "3": ("Monthly Summary (Bar)", lambda: Visualizer.monthly_summary(df)),
        "4": ("Expense Breakdown (Pie)", lambda: Visualizer.category_pie_chart(df, Category.EXPENSE.value)),
        "5": ("Income Breakdown (Pie)", lambda: Visualizer.category_pie_chart(df, Category.INCOME.value)),
        "6": ("Cumulative Savings (Area)", lambda: Visualizer.cumulative_savings(df)),
        "7": ("Full Dashboard", lambda: Visualizer.dashboard(df)),
    }

    while True:
        print("\n--- Visualization Menu ---")
        for key, (label, _) in menu_options.items():
            print(f"{key}. {label}")
        print("8. Back to Main Menu")

        choice = input("Choose a visualization (1-8): ").strip()

        if choice == "8":
            break
        if choice in menu_options:
            menu_options[choice][1]()
        else:
            print("Invalid choice.")


def main():
    store = TransactionStore()
    store.initialize()

    menu_options = {
        "1": ("Add a new transaction", lambda: add(store)),
        "2": ("View transactions and summary", lambda: store.get_transactions(
            get_date("Enter the start date (dd-mm-yyyy)"),
            get_date("Enter the end date (dd-mm-yyyy)"),
        )),
        "3": ("Visualize data", lambda: visualize_menu(store)),
    }

    while True:
        print("\n=== Personal Finance Tracker ===")
        for key, (label, _) in menu_options.items():
            print(f"{key}. {label}")
        print("4. Exit")

        choice = input("Enter your choice (1-4): ").strip()

        if choice == "4":
            print("Goodbye!")
            break
        if choice in menu_options:
            menu_options[choice][1]()
        else:
            print("Invalid choice. Please enter 1-4.")


if __name__ == "__main__":
    main()
