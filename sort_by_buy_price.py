import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def get_last_two_trading_days(ticker):
    end_date = datetime.now().date()
    for _ in range(10):  # Look back up to 10 days to handle long weekends/holidays
        data = yf.download(ticker, end=end_date + timedelta(days=1), period="7d", interval="1d", progress=False)
        if len(data) >= 2:
            return data.iloc[-1], data.iloc[-2]
        end_date -= timedelta(days=1)
    return None, None

def main():
    input_file = "tickers.csv"
    tickers = pd.read_csv(input_file)["Ticker"].dropna().unique()

    results = []
    for ticker in tickers:
        print(f"\n  ↳ {ticker}")
        try:
            latest, previous = get_last_two_trading_days(ticker)
            if latest is None or previous is None:
                print(f"    Skipped: not enough data")
                continue

            print(f"    Latest Date: {latest.name.date()}, Close: {latest['Close']}")
            print(f"    Previous Date: {previous.name.date()}, High: {previous['High']}")

            current_price = latest["Close"].item()
            yesterdays_high = previous["High"].item()

            # Safety check for NaN or missing values
            if pd.isna(current_price) or pd.isna(yesterdays_high) or yesterdays_high == 0:
                print(f"    Skipped: invalid data (Close or High missing/zero)")
                continue

            percent_diff = ((current_price - yesterdays_high) / yesterdays_high) * 100
            results.append({
                "Ticker": ticker,
                "Current Price": round(current_price, 2),
                "Yesterday's High": round(yesterdays_high, 2),
                "Percent Diff From High": round(percent_diff, 2)
            })

        except Exception as e:
            print(f"    Error: {e}")
            continue

    df_result = pd.DataFrame(results)

    if not df_result.empty:
        df_result.sort_values(by="Percent Diff From High", inplace=True)
        df_result.to_csv("sorted_tickers.csv", index=False)
        print("\n✅ Saved to sorted_tickers.csv")
    else:
        print("\n❌ No valid data to save. All entries were skipped due to missing/invalid fields.")


if __name__ == "__main__":
    main()
