import pandas as pd
import csv
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class CSV:
    CSV_FILE = "finance_data.csv"
    COLUMNS = ["date", "amount", "category", "description"]
    FORMAT = "%d-%m-%Y"

    @classmethod
    def initialize_csv(cls):
        if not os.path.exists(cls.CSV_FILE) or os.path.getsize(cls.CSV_FILE) == 0:
            df = pd.DataFrame(columns=cls.COLUMNS)
            df.to_csv(cls.CSV_FILE, index=False)
            print(f"Initialized {cls.CSV_FILE}")

    @classmethod
    def add_entry(cls, date, amount, category, description):
        new_entry = {
            'date': date,
            'amount': amount,
            'category': category,
            'description': description
        }
        with open(cls.CSV_FILE, "a", newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=cls.COLUMNS)
            writer.writerow(new_entry)
        print("Entry added successfully")

    @classmethod
    def get_transactions_df(cls, start_date=None, end_date=None):
        """Returns a DataFrame of transactions, optionally filtered by date range."""
        cls.initialize_csv()
        df = pd.read_csv(cls.CSV_FILE)

        if df.empty:
            return df

        df["date"] = pd.to_datetime(df["date"], format=cls.FORMAT, errors='coerce')
        df = df.dropna(subset=["date"])

        if start_date and end_date:
            start = datetime.strptime(start_date, cls.FORMAT)
            end = datetime.strptime(end_date, cls.FORMAT)
            mask = (df["date"] >= start) & (df["date"] <= end)
            df = df.loc[mask]

        return df.sort_values("date")

    @classmethod
    def get_transaction(cls, start_date, end_date):
        df = cls.get_transactions_df(start_date, end_date)

        if df.empty:
            print("No transactions found in the given date range.")
            return df

        print(f"\nTransactions from {start_date} to {end_date}")
        print(df.to_string(index=False, formatters={"date": lambda x: x.strftime(cls.FORMAT)}))

        total_income = df[df["category"] == "Income"]["amount"].sum()
        total_expense = df[df["category"] == "Expense"]["amount"].sum()
        print("\nSummary:")
        print(f"Total income: ${total_income:.2f}")
        print(f"Total expense: ${total_expense:.2f}")
        print(f"Net savings: ${(total_income - total_expense):.2f}")

        return df


class Visualizer:
    """Handles all Plotly visualizations for financial data."""

    @staticmethod
    def income_vs_expense_bar(df):
        """Bar chart comparing total income vs expense."""
        if df.empty:
            print("No data to visualize.")
            return

        summary = df.groupby("category")["amount"].sum().reset_index()

        fig = px.bar(
            summary,
            x="category",
            y="amount",
            color="category",
            color_discrete_map={"Income": "#2ecc71", "Expense": "#e74c3c"},
            title="Income vs Expense",
            labels={"amount": "Amount ($)", "category": "Category"}
        )
        fig.update_layout(showlegend=False)
        fig.show()

    @staticmethod
    def spending_over_time(df):
        """Line chart showing income and expenses over time."""
        if df.empty:
            print("No data to visualize.")
            return

        daily = df.groupby(["date", "category"])["amount"].sum().reset_index()

        fig = px.line(
            daily,
            x="date",
            y="amount",
            color="category",
            color_discrete_map={"Income": "#2ecc71", "Expense": "#e74c3c"},
            title="Transactions Over Time",
            labels={"amount": "Amount ($)", "date": "Date"},
            markers=True
        )
        fig.show()

    @staticmethod
    def monthly_summary(df):
        """Bar chart showing monthly income vs expense."""
        if df.empty:
            print("No data to visualize.")
            return

        df = df.copy()
        df["month"] = df["date"].dt.to_period("M").astype(str)

        monthly = df.groupby(["month", "category"])["amount"].sum().reset_index()

        fig = px.bar(
            monthly,
            x="month",
            y="amount",
            color="category",
            barmode="group",
            color_discrete_map={"Income": "#2ecc71", "Expense": "#e74c3c"},
            title="Monthly Income vs Expense",
            labels={"amount": "Amount ($)", "month": "Month"}
        )
        fig.show()

    @staticmethod
    def category_pie_chart(df, category="Expense"):
        """Pie chart showing breakdown by description for a category."""
        if df.empty:
            print("No data to visualize.")
            return

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
            hole=0.4
        )
        fig.show()

    @staticmethod
    def cumulative_savings(df):
        """Line chart showing cumulative savings over time."""
        if df.empty:
            print("No data to visualize.")
            return

        df = df.copy().sort_values("date")
        df["signed_amount"] = df.apply(
            lambda row: row["amount"] if row["category"] == "Income" else -row["amount"],
            axis=1
        )
        df["cumulative"] = df["signed_amount"].cumsum()

        fig = px.area(
            df,
            x="date",
            y="cumulative",
            title="Cumulative Savings Over Time",
            labels={"cumulative": "Savings ($)", "date": "Date"}
        )
        fig.update_traces(line_color="#3498db", fillcolor="rgba(52, 152, 219, 0.3)")
        fig.show()

    @staticmethod
    def dashboard(df):
        """Full dashboard with multiple charts."""
        if df.empty:
            print("No data to visualize.")
            return

        df = df.copy()
        df["month"] = df["date"].dt.to_period("M").astype(str)
        df["signed_amount"] = df.apply(
            lambda row: row["amount"] if row["category"] == "Income" else -row["amount"],
            axis=1
        )
        df["cumulative"] = df.sort_values("date")["signed_amount"].cumsum()

        # Summary stats
        total_income = df[df["category"] == "Income"]["amount"].sum()
        total_expense = df[df["category"] == "Expense"]["amount"].sum()
        net_savings = total_income - total_expense

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                "Income vs Expense",
                "Cumulative Savings",
                "Monthly Breakdown",
                "Expense by Description"
            ),
            specs=[
                [{"type": "bar"}, {"type": "scatter"}],
                [{"type": "bar"}, {"type": "pie"}]
            ]
        )

        # Income vs Expense bar
        summary = df.groupby("category")["amount"].sum().reset_index()
        colors = ["#2ecc71" if c == "Income" else "#e74c3c" for c in summary["category"]]
        fig.add_trace(
            go.Bar(x=summary["category"], y=summary["amount"], marker_color=colors, name="Total"),
            row=1, col=1
        )

        # Cumulative savings line
        sorted_df = df.sort_values("date")
        fig.add_trace(
            go.Scatter(
                x=sorted_df["date"], y=sorted_df["cumulative"],
                mode="lines+markers", name="Savings",
                line=dict(color="#3498db"), fill="tozeroy"
            ),
            row=1, col=2
        )

        # Monthly breakdown
        monthly = df.groupby(["month", "category"])["amount"].sum().reset_index()
        for cat, color in [("Income", "#2ecc71"), ("Expense", "#e74c3c")]:
            cat_data = monthly[monthly["category"] == cat]
            fig.add_trace(
                go.Bar(x=cat_data["month"], y=cat_data["amount"], name=cat, marker_color=color),
                row=2, col=1
            )

        # Expense pie chart
        expenses = df[df["category"] == "Expense"]
        if not expenses.empty:
            by_desc = expenses.groupby("description")["amount"].sum().reset_index()
            fig.add_trace(
                go.Pie(labels=by_desc["description"], values=by_desc["amount"], hole=0.4),
                row=2, col=2
            )

        fig.update_layout(
            height=800,
            title_text=f"Financial Dashboard | Income: ${total_income:,.2f} | Expense: ${total_expense:,.2f} | Net: ${net_savings:,.2f}",
            showlegend=True
        )
        fig.show()


# Data entry functions
def get_date(prompt, allow_default=False):
    date_str = input(f"{prompt}: ").strip()
    if allow_default and date_str == "":
        today = datetime.today().strftime(CSV.FORMAT)
        print(f"Using today's date: {today}")
        return today
    try:
        parsed = datetime.strptime(date_str, CSV.FORMAT)
        return parsed.strftime(CSV.FORMAT)
    except ValueError:
        print("Invalid date format. Please use dd-mm-yyyy (e.g., 19-12-2025)")
        return get_date(prompt, allow_default)


def get_amount():
    try:
        amount = float(input("Enter the amount: "))
        if amount <= 0:
            raise ValueError("Amount must be positive.")
        return amount
    except ValueError as e:
        print(e)
        return get_amount()


def get_category():
    category = input("Enter the category ('I' for Income or 'E' for Expense): ").upper()
    if category == "I":
        return "Income"
    elif category == "E":
        return "Expense"
    else:
        print("Invalid category. Please enter 'I' or 'E'.")
        return get_category()


def get_description():
    return input("Enter a description (optional): ").strip()


def add():
    CSV.initialize_csv()
    date = get_date("Enter the date (dd-mm-yyyy) or press Enter for today", allow_default=True)
    amount = get_amount()
    category = get_category()
    description = get_description()
    CSV.add_entry(date, amount, category, description)


def visualize_menu():
    """Sub-menu for visualization options."""
    start_date = get_date("Enter start date (dd-mm-yyyy)")
    end_date = get_date("Enter end date (dd-mm-yyyy)")
    df = CSV.get_transactions_df(start_date, end_date)

    if df.empty:
        print("No data to visualize for this date range.")
        return

    while True:
        print("\n--- Visualization Menu ---")
        print("1. Income vs Expense (Bar)")
        print("2. Transactions Over Time (Line)")
        print("3. Monthly Summary (Bar)")
        print("4. Expense Breakdown (Pie)")
        print("5. Income Breakdown (Pie)")
        print("6. Cumulative Savings (Area)")
        print("7. Full Dashboard")
        print("8. Back to Main Menu")

        choice = input("Choose a visualization (1-8): ").strip()

        if choice == "1":
            Visualizer.income_vs_expense_bar(df)
        elif choice == "2":
            Visualizer.spending_over_time(df)
        elif choice == "3":
            Visualizer.monthly_summary(df)
        elif choice == "4":
            Visualizer.category_pie_chart(df, "Expense")
        elif choice == "5":
            Visualizer.category_pie_chart(df, "Income")
        elif choice == "6":
            Visualizer.cumulative_savings(df)
        elif choice == "7":
            Visualizer.dashboard(df)
        elif choice == "8":
            break
        else:
            print("Invalid choice.")


def main():
    CSV.initialize_csv()

    while True:
        print("\n=== Personal Finance Tracker ===")
        print("1. Add a new transaction")
        print("2. View transactions and summary")
        print("3. Visualize data")
        print("4. Exit")

        choice = input("Enter your choice (1-4): ").strip()

        if choice == "1":
            add()
        elif choice == "2":
            start_date = get_date("Enter the start date (dd-mm-yyyy)")
            end_date = get_date("Enter the end date (dd-mm-yyyy)")
            CSV.get_transaction(start_date, end_date)
        elif choice == "3":
            visualize_menu()
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1-4.")


if __name__ == "__main__":
    main()