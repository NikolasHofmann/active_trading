import csv
import os
import yfinance as yf

FILENAME = "trades_log.csv"

def ensure_file_exists():
    if not os.path.exists(FILENAME):
        with open(FILENAME, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Ticker", "Quantity", "Buy Price", "Sell Price", "Profit (USD)", "Profit (%)"])

def generate_trade_id():
    with open(FILENAME, mode='r') as file:
        reader = csv.reader(file)
        next(reader)
        ids = [int(row[0]) for row in reader]
        return max(ids) + 1 if ids else 1

def add_trade():
    ticker = input("Enter stock ticker: ").upper()
    quantity = float(input("Enter number of stocks bought: "))
    buy_price = float(input("Enter buy price per stock: "))
    sell_price_input = input("Enter sell price per stock (or leave blank if not sold yet): ")

    if sell_price_input.strip():
        sell_price = float(sell_price_input)
        profit_usd = (sell_price - buy_price) * quantity
        invested = buy_price * quantity
        profit_pct = (profit_usd / invested) * 100 if invested else 0
    else:
        sell_price = "None"
        profit_usd = ""
        profit_pct = ""

    trade_id = generate_trade_id()

    with open(FILENAME, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([trade_id, ticker, quantity, buy_price, sell_price, profit_usd, profit_pct])

    print(f"\nTrade added with ID {trade_id}.")

def display_trades(open_only=False):
    ensure_file_exists()
    total_trades = 0
    total_realized_profit = 0.0
    total_unrealized_profit = 0.0

    # Read all rows
    with open(FILENAME, mode='r') as file:
        reader = csv.reader(file)
        rows = list(reader)

    if len(rows) <= 1:
        print("\n--- Trade Log ---")
        print("No trades logged yet.")
        return

    header = rows[0]
    # Prepare a list of rows (as lists of strings) to be printed
    table = []
    table.append(header.copy())  # start with header

    for row in rows[1:]:
        sell_price = row[4]
        ticker = row[1]
        quantity = float(row[2])
        buy_price = float(row[3])

        # Initialize display strings
        id_str       = str(row[0])
        ticker_str   = ticker
        qty_str      = f"{quantity:.3f}"
        buy_str      = f"{buy_price:.3f}"
        sell_str     = ""
        profit_usd_s = ""
        profit_pct_s = ""

        if sell_price == "None":
            # Open trade
            try:
                current_price = yf.Ticker(ticker).history(period='1d')['Close'].iloc[-1]
                profit_usd = (current_price - buy_price) * quantity
                invested = buy_price * quantity
                profit_pct = (profit_usd / invested) * 100 if invested else 0

                sell_str     = f"{current_price:.3f} (LIVE)"
                profit_usd_s = f"{profit_usd:.3f}"
                profit_pct_s = f"{profit_pct:.3f}%"
                total_unrealized_profit += profit_usd
            except:
                sell_str     = "N/A"
                profit_usd_s = "N/A"
                profit_pct_s = "N/A"
        else:
            # Closed trade
            try:
                sell_val     = float(sell_price)
                profit_usd   = float(row[5])
                profit_pct   = float(row[6])
                sell_str     = f"{sell_val:.3f}"
                profit_usd_s = f"{profit_usd:.3f}"
                profit_pct_s = f"{profit_pct:.3f}%"
                total_realized_profit += profit_usd
            except:
                sell_str     = sell_price
                profit_usd_s = row[5]
                profit_pct_s = row[6]

        if open_only and sell_price != "None":
            continue  # skip closed trades if only open trades requested

        total_trades += 1
        table.append([id_str, ticker_str, qty_str, buy_str, sell_str, profit_usd_s, profit_pct_s])

    # Compute column widths
    num_cols = len(table[0])
    col_widths = [0] * num_cols
    for r in table:
        for i, cell in enumerate(r):
            col_widths[i] = max(col_widths[i], len(cell))

    # Print header separator
    sep_parts = []
    for w in col_widths:
        sep_parts.append("-" * (w + 2))
    separator = "+" + "+".join(sep_parts) + "+"

    # Print neatly
    print("\n--- Trade Log ---")
    print(separator)
    # Header row
    header_row = "|"
    for i, cell in enumerate(table[0]):
        header_row += " " + cell.ljust(col_widths[i]) + " |"
    print(header_row)
    print(separator)

    # Data rows
    for r in table[1:]:
        row_str = "|"
        for i, cell in enumerate(r):
            row_str += " " + cell.ljust(col_widths[i]) + " |"
        print(row_str)
    print(separator)

    # Totals
    if not open_only:
        print(f"Total trades shown: {total_trades}")
        print(f"Total realized P/L: ${total_realized_profit:.3f}")
        print(f"Total unrealized P/L (open trades): ${total_unrealized_profit:.3f}")
        print(f"Net total (realized + unrealized): ${total_realized_profit + total_unrealized_profit:.3f}")
    else:
        print(f"Total open trades shown: {total_trades}")
        print(f"Total unrealized P/L (open trades): ${total_unrealized_profit:.3f}")

def complete_trade():
    ticker = input("Enter stock ticker: ").upper()
    id_input = input("Enter trade ID to complete (leave blank to auto-complete latest open trade for ticker): ").strip()
    sell_price = float(input("Enter sell price per stock: "))

    with open(FILENAME, mode='r') as file:
        rows = list(csv.reader(file))

    header = rows[0]
    updated = False

    if id_input:
        target_id = int(id_input)
        for row in rows[1:]:
            if int(row[0]) == target_id and row[4] == "None":
                quantity = float(row[2])
                buy_price = float(row[3])
                profit_usd = (sell_price - buy_price) * quantity
                invested = buy_price * quantity
                profit_pct = (profit_usd / invested) * 100 if invested else 0

                row[4] = f"{sell_price}"
                row[5] = f"{profit_usd:.3f}"
                row[6] = f"{profit_pct:.3f}"
                updated = True
                break
    else:
        # Find last open trade for ticker
        for row in reversed(rows[1:]):
            if row[1] == ticker and row[4] == "None":
                quantity = float(row[2])
                buy_price = float(row[3])
                profit_usd = (sell_price - buy_price) * quantity
                invested = buy_price * quantity
                profit_pct = (profit_usd / invested) * 100 if invested else 0

                row[4] = f"{sell_price}"
                row[5] = f"{profit_usd:.3f}"
                row[6] = f"{profit_pct:.3f}"
                updated = True
                break

    if updated:
        with open(FILENAME, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerows(rows[1:])
        print("Trade completed successfully.")
    else:
        print("Could not find matching open trade to update.")

def delete_trade():
    display_trades()
    try:
        trade_id = input("\nEnter ID of trade to delete (or 'cancel' to go back): ").strip()
        if trade_id.lower() == 'cancel':
            return

        trade_id = int(trade_id)
        with open(FILENAME, mode='r') as file:
            rows = list(csv.reader(file))

        header = rows[0]
        new_rows = [row for row in rows[1:] if int(row[0]) != trade_id]

        if len(new_rows) != len(rows) - 1:
            with open(FILENAME, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(header)
                writer.writerows(new_rows)
            print(f"Trade with ID {trade_id} deleted.")
        else:
            print("Trade ID not found.")
    except ValueError:
        print("Invalid input. Please enter a valid trade ID.")

def main():
    ensure_file_exists()

    while True:
        print("\n--- Trade Logger ---")
        print("1. Add new trade")
        print("2. View all trades")
        print("3. View open trades with current profit/loss")
        print("4. Complete an open trade (enter sell price)")
        print("5. Delete a trade")
        print("6. Exit")

        choice = input("Choose an option: ").strip()

        if choice == '1':
            add_trade()
        elif choice == '2':
            display_trades(open_only=False)
        elif choice == '3':
            display_trades(open_only=True)
        elif choice == '4':
            complete_trade()
        elif choice == '5':
            delete_trade()
        elif choice == '6':
            print("Exiting...")
            break
        else:
            print("Invalid option. Please choose again.")

if __name__ == "__main__":
    main()
