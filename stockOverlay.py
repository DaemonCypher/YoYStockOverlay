import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

def aggregate_monthly_data(df):
    monthly_data = []

    # Group data by year and month
    grouped = df.groupby([df.index.year, df.index.month])

    for (year, month), group in grouped:
        open_price = group['Adj Close'].iloc[0]
        high_price = group['Adj Close'].max()
        low_price = group['Adj Close'].min()
        close_price = group['Adj Close'].iloc[-1]
        monthly_data.append({
            'Date': pd.Timestamp(year=year, month=month, day=1),
            'Open': open_price,
            'High': high_price,
            'Low': low_price,
            'Close': close_price
        })

    return pd.DataFrame(monthly_data).set_index('Date')

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
            
            # Calculate the percent change from the start of the year using 'Adj Close'
            start_price = stock_data['Adj Close'].iloc[0]
            stock_data['Percent Change'] = ((stock_data['Adj Close'] - start_price) / start_price) * 100
            
            all_stock_data = pd.concat([all_stock_data, stock_data])

            # Calculate annual percent change
            annual_open = stock_data['Adj Close'].iloc[0]
            annual_close = stock_data['Adj Close'].iloc[-1]
            annual_percent_change = ((annual_close - annual_open) / annual_open) * 100
            annual_percent_changes[year] = annual_percent_change

            # Plot stock data with annual percent change in the legend
            plt.plot(stock_data['Normalized Date'], stock_data['Percent Change'], 
                     label=f"{year} ({annual_percent_change:.2f}%)")
        else:
            print(f"No data for year {year}")
            
    # Resample the data to monthly frequency using the first and last values for 'Adj Close'
    monthly_data= aggregate_monthly_data(all_stock_data)

    # Calculate percent change based on 'Adj Close' values
    monthly_data['Percent Change'] = ((monthly_data['Close'] - monthly_data['Open']) / monthly_data['Open']) * 100

    # Print quarterly percent change for the year 2000
    print("\nQuarterly Percent Change for the Year 2000:")
    for start, end in [('01-01', '03-31'), ('04-01', '06-30'), ('07-01', '09-30'), ('10-01', '12-31')]:
        quarter_data = monthly_data[(monthly_data.index.month >= int(start.split('-')[0])) & (monthly_data.index.month <= int(end.split('-')[0]))]
        avg_percent_change = quarter_data['Percent Change'].mean()
        print(f"Quarter {start[:2]}-{end[:2]}: {avg_percent_change:.2f}%")

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
# 2001, 2002, 2008, 2007, 2020
plot_stock_movements('SPY', 2013, 2023, exclude_years=[2001, 2002, 2008, 2007, 2020])
