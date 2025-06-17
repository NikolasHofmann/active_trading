import csv

OLD_FILE = "trades_log.csv"
NEW_FILE = "trades_log_migrated.csv"

with open(OLD_FILE, mode='r') as infile, open(NEW_FILE, mode='w', newline='') as outfile:
    reader = csv.DictReader(infile)
    fieldnames = ["ID", "Ticker", "Quantity", "Buy Price", "Total Sold", "Total Received", "Avg Sell Price", "Profit (USD)", "Profit (%)"]
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        new_row = {
            "ID": row["ID"],
            "Ticker": row["Ticker"],
            "Quantity": row["Quantity"],
            "Buy Price": row["Buy Price"],
        }

        sell_price = row["Sell Price"]
        quantity = float(row["Quantity"])
        buy_price = float(row["Buy Price"])

        if sell_price == "None":
            # Open trade
            new_row.update({
                "Total Sold": 0,
                "Total Received": 0,
                "Avg Sell Price": "None",
                "Profit (USD)": "",
                "Profit (%)": ""
            })
        else:
            # Closed trade
            sell_price = float(sell_price)
            total_received = sell_price * quantity
            profit_usd = float(row["Profit (USD)"]) if row["Profit (USD)"] else (sell_price - buy_price) * quantity
            invested = buy_price * quantity
            profit_pct = (profit_usd / invested) * 100 if invested else 0

            new_row.update({
                "Total Sold": quantity,
                "Total Received": total_received,
                "Avg Sell Price": f"{sell_price:.3f}",
                "Profit (USD)": f"{profit_usd:.3f}",
                "Profit (%)": f"{profit_pct:.2f}"
            })

        writer.writerow(new_row)

print("Migration complete. Output written to", NEW_FILE)
