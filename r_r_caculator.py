import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

def get_previous_day_data(ticker: str):
    end_date = datetime.today()
    start_date = end_date - timedelta(days=7)  # buffer for weekends/holidays

    df = yf.download(ticker, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))

    if df.empty:
        raise ValueError(f"No data found for {ticker}")

    print(f"Columns type: {type(df.columns)}")
    print(f"Columns: {df.columns}")

    # Handle multi-index columns
    if isinstance(df.columns, pd.MultiIndex):
        # Try to extract ticker data
        if ticker in df.columns.levels[1]:
            df = df.xs(ticker, axis=1, level=1)  # extract columns for this ticker only
        else:
            # fallback to just use df as is
            df = df.iloc[:, :]

    else:
        # Single ticker, columns are regular
        df = df.iloc[:, :]

    prev_day = df.iloc[-1]
    return prev_day

def get_float_input(prompt, default_value):
    while True:
        user_input = input(prompt)
        if user_input.strip() == '':
            return default_value
        try:
            return float(user_input)
        except ValueError:
            print("❌ Invalid number entered. Please try again.")

def main():
    print("📈 Stock Trade Recorder")
    ticker = input("Enter stock ticker (e.g. AAPL): ").strip().upper()

    try:
        prev_day = get_previous_day_data(ticker)
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return

    # Extract scalar prices from multi-index series if needed
    # Check if prev_day items are Series (multi-index case) or floats (single)
    def extract_scalar(value):
        if isinstance(value, pd.Series):
            # Expect ticker key present
            if ticker in value:
                return float(value[ticker])
            else:
                # fallback - take first item if ticker missing
                return float(value.iloc[0])
        else:
            return float(value)

    open_price = extract_scalar(prev_day['Open'])
    high_price = extract_scalar(prev_day['High'])
    low_price = extract_scalar(prev_day['Low'])
    close_price = extract_scalar(prev_day['Close'])

    print(f"\n📅 Previous day ({prev_day.name.date()}) data for {ticker}:")
    print(f"   Open:  {open_price:.2f}")
    print(f"   High:  {high_price:.2f}")
    print(f"   Low:   {low_price:.2f}")
    print(f"   Close: {close_price:.2f}")

    try:
        # buy_price = get_float_input(
        #     f"Enter buy price (leave blank to use High + 0.01): ",
        #     round(high_price + 0.01, 2)
        # )
        # stop_loss = get_float_input(
        #     f"Enter stop loss (leave blank to use Low - 0.01): ",
        #     round(low_price - 0.01, 2)
        # )

        buy_price = round(high_price + 0.01, 2)
        stop_loss = round(low_price - 0.01, 2)

        risk_per_share = round(buy_price - stop_loss, 2)
        if risk_per_share <= 0:
            print("❌ Stop loss must be below buy price.")
            return

        total_risk = 1.00  # You can make this user-configurable if desired
        shares_to_buy = int(total_risk // risk_per_share)

        min_sell_price = round(buy_price + risk_per_share, 2)

        print(f"\n✅ Trade summary:")
        print(f"   Buy price:       {buy_price:.2f}")
        print(f"   Stop loss:       {stop_loss:.2f}")
        print(f"   Risk per share:  {risk_per_share:.2f}")
        print(f"   Min sell price (1:1 R:R): {min_sell_price:.2f}")
        print(f"   Max total risk:  ${total_risk:.2f}")
        print(f"   ➤ Shares to buy: {shares_to_buy} share(s)")

    except ValueError:
        print("❌ Invalid number entered. Please try again.")

if __name__ == "__main__":
    main()
