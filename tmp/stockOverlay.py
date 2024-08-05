import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

def plot_stock_movements(ticker, start_year, end_year, exclude_years):
    plt.figure(figsize=(12, 6))

    all_stock_data = pd.DataFrame()
    annual_percent_changes = {}

    for year in range(start_year, end_year + 1):
        if year in exclude_years:
            continue

        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"
        stock_data = yf.download(ticker, start=start_date, end=end_date)

        if not stock_data.empty:
            # Normalize the dates to a common year (e.g., 2000) for plotting purposes
            stock_data['Normalized Date'] = stock_data.index.map(lambda x: x.replace(year=2000))
            all_stock_data = pd.concat([all_stock_data, stock_data])

            # Calculate annual percent change
            annual_open = stock_data['Open'].iloc[0]
            annual_close = stock_data['Close'].iloc[-1]
            annual_percent_change = ((annual_close - annual_open) / annual_open) * 100
            annual_percent_changes[year] = annual_percent_change

            # Plot stock data with annual percent change in the legend
            plt.plot(stock_data['Normalized Date'], stock_data['Close'], 
                     label=f"{year} ({annual_percent_change:.2f}%)")
        else:
            print(f"No data for year {year}")

    # Resample the data to monthly frequency using the first and last values for Open and Close
    monthly_data = all_stock_data.resample('ME').apply({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last'
    })
    
    
    # Calculate percent change based on Open and Close values
    monthly_data['Percent Change'] = ((monthly_data['Close'] - monthly_data['Open']) / monthly_data['Open']) * 100

    # Plot the stock movements and highlight each quarter
    quarters = {
        'Q1': ('01-01', '03-31'),
        'Q2': ('04-01', '06-30'),
        'Q3': ('07-01', '09-30'),
        'Q4': ('10-01', '12-31')
    }

    for quarter, (start, end) in quarters.items():
        quarter_data = monthly_data[(monthly_data.index.month >= int(start.split('-')[0])) & (monthly_data.index.month <= int(end.split('-')[0]))]

        if not quarter_data.empty:
            avg_percent_change = quarter_data['Percent Change'].mean()
            color = 'green' if avg_percent_change > 0 else 'red'
            plt.axvspan(f"2000-{start}", f"2000-{end}", color=color, alpha=0.3, label=f'{quarter} ({avg_percent_change:.2f}%)')

    plt.title(f"{ticker} Stock Movements (Percent Change) ({start_year} - {end_year})")
    plt.xlabel("Month")
    plt.ylabel("Percent Change")
    plt.legend(title='Yearly Gain')
    plt.grid(True)
    plt.xticks(pd.date_range("2000-01-01", "2000-12-31", freq='MS').to_pydatetime(),
               ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    plt.show()

# Example usage
#2001, 2008, 2007, 2020
plot_stock_movements('SPY', 1990, 2023, exclude_years=[2001, 2008, 2007, 2020])
