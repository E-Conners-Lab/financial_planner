# Personal Finance Tracker

A command-line personal finance management application with interactive data visualizations built using Python, Pandas, and Plotly.

## Features

- **Transaction Management**: Add and track income and expense transactions
- **Date Filtering**: View transactions within specific date ranges
- **Financial Summaries**: Automatic calculation of total income, expenses, and net savings
- **Interactive Visualizations**:
  - Income vs Expense bar charts
  - Transactions over time line charts
  - Monthly income/expense breakdowns
  - Expense/Income breakdown pie charts
  - Cumulative savings area charts
  - Full financial dashboard with multiple charts

## Requirements

- Python 3.x
- pandas
- plotly

## Installation

1. Clone or download this repository
2. Create a virtual environment (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   # or
   .venv\Scripts\activate     # On Windows
   ```
3. Install dependencies:
   ```bash
   pip install pandas plotly
   ```

## Usage

### Main Application

Run the main finance tracker:

```bash
python main.py
```

This opens an interactive menu with the following options:

1. **Add a new transaction** - Record income or expenses with date, amount, category, and description
2. **View transactions and summary** - Display transactions within a date range with totals
3. **Visualize data** - Open the visualization submenu
4. **Exit** - Close the application

### Visualization Menu

When you select "Visualize data", you can choose from:

1. Income vs Expense (Bar)
2. Transactions Over Time (Line)
3. Monthly Summary (Bar)
4. Expense Breakdown (Pie)
5. Income Breakdown (Pie)
6. Cumulative Savings (Area)
7. Full Dashboard (all charts combined)

### Demo Mode

To generate sample data and explore visualizations:

```bash
python generate_data.py
```

This script generates realistic financial data over 6 months (configurable) including:
- Monthly salary income
- Various expense categories (rent, groceries, utilities, entertainment, etc.)
- Random additional income sources

## Data Format

Transactions are stored in `finance_data.csv` with the following columns:

| Column      | Description                          |
|-------------|--------------------------------------|
| date        | Transaction date (dd-mm-yyyy format) |
| amount      | Transaction amount (positive number) |
| category    | "Income" or "Expense"                |
| description | Optional description of transaction  |

## Examples

### Adding a Transaction

```
Enter the date (dd-mm-yyyy) or press Enter for today: 19-12-2025
Enter the amount: 150.00
Enter the category ('I' for Income or 'E' for Expense): E
Enter a description (optional): Grocery shopping
Entry added successfully
```

### Viewing Transactions

```
Transactions from 01-12-2025 to 31-12-2025
       date  amount category     description
19-12-2025  150.00  Expense  Grocery shopping
...

Summary:
Total income: $5000.00
Total expense: $2500.00
Net savings: $2500.00
```

## Project Structure

```
financial_planner/
├── main.py           # Main application
├── generate_data.py  # Sample data generator and demo
├── finance_data.csv  # Transaction data (created on first run)
└── README.md
```