"""
Finance Tracker Demo Script
Generates realistic sample financial data and launches visualizations for demonstration.
"""

import pandas as pd
import csv
import os
import random
from datetime import datetime, timedelta
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

    @classmethod
    def get_transactions_df(cls, start_date=None, end_date=None):
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


class DemoDataGenerator:
    """Generates realistic sample financial transactions."""

    INCOME_SOURCES = [
        ("Salary", 4500, 5500),
        ("Freelance Project", 500, 2000),
        ("YouTube Revenue", 50, 300),
        ("Consulting", 200, 800),
        ("Dividends", 50, 200),
        ("Side Gig", 100, 500),
    ]

    EXPENSE_CATEGORIES = [
        ("Rent", 1200, 1800),
        ("Groceries", 80, 200),
        ("Gas", 40, 80),
        ("Electric Bill", 80, 150),
        ("Internet", 60, 100),
        ("Phone Bill", 50, 90),
        ("Dining Out", 20, 80),
        ("Coffee", 5, 15),
        ("Gym Membership", 30, 50),
        ("Streaming Services", 15, 45),
        ("Car Insurance", 100, 200),
        ("Health Insurance", 200, 400),
        ("Amazon Purchase", 20, 150),
        ("Gas Station", 30, 70),
        ("Uber/Lyft", 15, 50),
        ("Clothing", 30, 150),
        ("Home Supplies", 20, 80),
        ("Haircut", 25, 50),
        ("Pet Supplies", 30, 80),
        ("Entertainment", 20, 100),
        ("Software Subscription", 10, 50),
        ("Lab Equipment", 50, 200),
        ("Books/Courses", 20, 100),
    ]

    @classmethod
    def generate_sample_data(cls, months=6, filename="finance_data.csv"):
        """Generate sample financial data for the specified number of months."""
        transactions = []
        today = datetime.today()
        start_date = today - timedelta(days=months * 30)

        current_date = start_date

        while current_date <= today:
            # Monthly income (1st of month)
            if current_date.day == 1:
                # Primary salary
                transactions.append({
                    "date": current_date.strftime(CSV.FORMAT),
                    "amount": round(random.uniform(4500, 5500), 2),
                    "category": "Income",
                    "description": "Salary"
                })

                # Random additional income (50% chance)
                if random.random() > 0.5:
                    source = random.choice(cls.INCOME_SOURCES[1:])
                    transactions.append({
                        "date": current_date.strftime(CSV.FORMAT),
                        "amount": round(random.uniform(source[1], source[2]), 2),
                        "category": "Income",
                        "description": source[0]
                    })

            # Monthly bills (various days)
            if current_date.day == 1:
                transactions.append({
                    "date": current_date.strftime(CSV.FORMAT),
                    "amount": round(random.uniform(1200, 1800), 2),
                    "category": "Expense",
                    "description": "Rent"
                })

            if current_date.day == 5:
                transactions.append({
                    "date": current_date.strftime(CSV.FORMAT),
                    "amount": round(random.uniform(80, 150), 2),
                    "category": "Expense",
                    "description": "Electric Bill"
                })

            if current_date.day == 10:
                transactions.append({
                    "date": current_date.strftime(CSV.FORMAT),
                    "amount": round(random.uniform(60, 100), 2),
                    "category": "Expense",
                    "description": "Internet"
                })

            if current_date.day == 15:
                transactions.append({
                    "date": current_date.strftime(CSV.FORMAT),
                    "amount": round(random.uniform(100, 200), 2),
                    "category": "Expense",
                    "description": "Car Insurance"
                })

            # Random daily expenses (70% chance each day)
            if random.random() > 0.3:
                num_expenses = random.randint(1, 3)
                daily_expenses = random.sample(
                    [e for e in cls.EXPENSE_CATEGORIES if e[0] not in ["Rent", "Electric Bill", "Internet", "Car Insurance"]],
                    min(num_expenses, 5)
                )

                for expense in daily_expenses:
                    transactions.append({
                        "date": current_date.strftime(CSV.FORMAT),
                        "amount": round(random.uniform(expense[1], expense[2]), 2),
                        "category": "Expense",
                        "description": expense[0]
                    })

            current_date += timedelta(days=1)

        # Write to CSV
        df = pd.DataFrame(transactions)
        df.to_csv(filename, index=False)

        print(f"✅ Generated {len(transactions)} transactions over {months} months")
        print(f"📁 Saved to: {filename}")

        return df


class Visualizer:
    """Handles all Plotly visualizations for financial data."""

    @staticmethod
    def income_vs_expense_bar(df):
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
            title="💰 Total Income vs Expense",
            labels={"amount": "Amount ($)", "category": "Category"}
        )
        fig.update_layout(showlegend=False, template="plotly_dark")
        fig.show()

    @staticmethod
    def spending_over_time(df):
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
            title="📈 Transactions Over Time",
            labels={"amount": "Amount ($)", "date": "Date"},
            markers=True
        )
        fig.update_layout(template="plotly_dark")
        fig.show()

    @staticmethod
    def monthly_summary(df):
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
            title="📊 Monthly Income vs Expense",
            labels={"amount": "Amount ($)", "month": "Month"}
        )
        fig.update_layout(template="plotly_dark")
        fig.show()

    @staticmethod
    def expense_breakdown_pie(df):
        if df.empty:
            print("No data to visualize.")
            return

        expenses = df[df["category"] == "Expense"]
        if expenses.empty:
            print("No expense data to visualize.")
            return

        by_desc = expenses.groupby("description")["amount"].sum().reset_index()
        by_desc = by_desc.sort_values("amount", ascending=False).head(10)

        fig = px.pie(
            by_desc,
            values="amount",
            names="description",
            title="🥧 Top 10 Expense Categories",
            hole=0.4
        )
        fig.update_layout(template="plotly_dark")
        fig.show()

    @staticmethod
    def cumulative_savings(df):
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
            title="📈 Cumulative Savings Over Time",
            labels={"cumulative": "Savings ($)", "date": "Date"}
        )
        fig.update_traces(line_color="#3498db", fillcolor="rgba(52, 152, 219, 0.3)")
        fig.update_layout(template="plotly_dark")
        fig.show()

    @staticmethod
    def top_expenses_bar(df):
        if df.empty:
            print("No data to visualize.")
            return

        expenses = df[df["category"] == "Expense"]
        by_desc = expenses.groupby("description")["amount"].sum().reset_index()
        by_desc = by_desc.sort_values("amount", ascending=True).tail(10)

        fig = px.bar(
            by_desc,
            x="amount",
            y="description",
            orientation="h",
            title="🔝 Top 10 Expenses by Category",
            labels={"amount": "Total Amount ($)", "description": "Category"},
            color="amount",
            color_continuous_scale="Reds"
        )
        fig.update_layout(template="plotly_dark", showlegend=False)
        fig.show()

    @staticmethod
    def dashboard(df):
        if df.empty:
            print("No data to visualize.")
            return

        df = df.copy()
        df["month"] = df["date"].dt.to_period("M").astype(str)
        df["signed_amount"] = df.apply(
            lambda row: row["amount"] if row["category"] == "Income" else -row["amount"],
            axis=1
        )
        df_sorted = df.sort_values("date").copy()
        df_sorted["cumulative"] = df_sorted["signed_amount"].cumsum()

        total_income = df[df["category"] == "Income"]["amount"].sum()
        total_expense = df[df["category"] == "Expense"]["amount"].sum()
        net_savings = total_income - total_expense

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                "Income vs Expense",
                "Cumulative Savings",
                "Monthly Breakdown",
                "Top Expense Categories"
            ),
            specs=[
                [{"type": "bar"}, {"type": "scatter"}],
                [{"type": "bar"}, {"type": "pie"}]
            ],
            vertical_spacing=0.12,
            horizontal_spacing=0.1
        )

        # Income vs Expense
        summary = df.groupby("category")["amount"].sum().reset_index()
        colors = ["#2ecc71" if c == "Income" else "#e74c3c" for c in summary["category"]]
        fig.add_trace(
            go.Bar(x=summary["category"], y=summary["amount"], marker_color=colors, name="Total"),
            row=1, col=1
        )

        # Cumulative savings
        fig.add_trace(
            go.Scatter(
                x=df_sorted["date"], y=df_sorted["cumulative"],
                mode="lines", name="Savings",
                line=dict(color="#3498db", width=2), fill="tozeroy",
                fillcolor="rgba(52, 152, 219, 0.3)"
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

        # Expense pie
        expenses = df[df["category"] == "Expense"]
        if not expenses.empty:
            by_desc = expenses.groupby("description")["amount"].sum().reset_index()
            by_desc = by_desc.sort_values("amount", ascending=False).head(8)
            fig.add_trace(
                go.Pie(
                    labels=by_desc["description"],
                    values=by_desc["amount"],
                    hole=0.4,
                    textinfo="percent+label",
                    textposition="inside"
                ),
                row=2, col=2
            )

        savings_color = "#2ecc71" if net_savings >= 0 else "#e74c3c"
        fig.update_layout(
            height=900,
            title_text=f"<b>📊 Personal Finance Dashboard</b><br><sup>Income: ${total_income:,.2f} | Expense: ${total_expense:,.2f} | Net: <span style='color:{savings_color}'>${net_savings:,.2f}</span></sup>",
            template="plotly_dark",
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig.show()


def print_summary(df):
    """Print a text summary of the financial data."""
    if df.empty:
        print("No data available.")
        return

    total_income = df[df["category"] == "Income"]["amount"].sum()
    total_expense = df[df["category"] == "Expense"]["amount"].sum()
    net_savings = total_income - total_expense

    num_transactions = len(df)
    date_range = f"{df['date'].min().strftime('%d-%m-%Y')} to {df['date'].max().strftime('%d-%m-%Y')}"

    print("\n" + "=" * 50)
    print("📊 FINANCIAL SUMMARY")
    print("=" * 50)
    print(f"📅 Date Range: {date_range}")
    print(f"📝 Total Transactions: {num_transactions}")
    print("-" * 50)
    print(f"💵 Total Income:  ${total_income:>12,.2f}")
    print(f"💸 Total Expense: ${total_expense:>12,.2f}")
    print("-" * 50)
    if net_savings >= 0:
        print(f"✅ Net Savings:   ${net_savings:>12,.2f}")
    else:
        print(f"❌ Net Loss:      ${net_savings:>12,.2f}")
    print("=" * 50)

    # Top 5 expenses
    expenses = df[df["category"] == "Expense"]
    if not expenses.empty:
        top_expenses = expenses.groupby("description")["amount"].sum().sort_values(ascending=False).head(5)
        print("\n🔝 Top 5 Expense Categories:")
        for i, (desc, amt) in enumerate(top_expenses.items(), 1):
            print(f"   {i}. {desc}: ${amt:,.2f}")


def demo_menu():
    """Interactive demo menu."""
    print("\n" + "=" * 50)
    print("🎬 FINANCE TRACKER DEMO")
    print("=" * 50)

    # Check if data exists
    if not os.path.exists("finance_data.csv") or os.path.getsize("finance_data.csv") == 0:
        print("\n📊 No data found. Generating sample data...")
        DemoDataGenerator.generate_sample_data(months=6)

    df = CSV.get_transactions_df()

    while True:
        print("\n--- Demo Menu ---")
        print("1. 📊 Generate New Sample Data")
        print("2. 📋 View Data Summary")
        print("3. 💰 Income vs Expense (Bar)")
        print("4. 📈 Transactions Over Time (Line)")
        print("5. 📊 Monthly Summary (Bar)")
        print("6. 🥧 Expense Breakdown (Pie)")
        print("7. 🔝 Top Expenses (Horizontal Bar)")
        print("8. 📈 Cumulative Savings (Area)")
        print("9. 🎯 Full Dashboard (All Charts)")
        print("0. 🚪 Exit")

        choice = input("\nChoose an option (0-9): ").strip()

        if choice == "1":
            months = input("How many months of data? (default: 6): ").strip()
            months = int(months) if months.isdigit() else 6
            DemoDataGenerator.generate_sample_data(months=months)
            df = CSV.get_transactions_df()

        elif choice == "2":
            print_summary(df)

        elif choice == "3":
            Visualizer.income_vs_expense_bar(df)

        elif choice == "4":
            Visualizer.spending_over_time(df)

        elif choice == "5":
            Visualizer.monthly_summary(df)

        elif choice == "6":
            Visualizer.expense_breakdown_pie(df)

        elif choice == "7":
            Visualizer.top_expenses_bar(df)

        elif choice == "8":
            Visualizer.cumulative_savings(df)

        elif choice == "9":
            Visualizer.dashboard(df)

        elif choice == "0":
            print("\n👋 Thanks for checking out the Finance Tracker!")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    demo_menu()