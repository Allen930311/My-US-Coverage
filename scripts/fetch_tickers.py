import pandas as pd

def fetch_tickers():
    print("Fetching US tickers...")
    
    # DataHub.io sources for NASDAQ and NYSE
    nasdaq_url = "https://datahub.io/core/nasdaq-listings/_r/-/data/nasdaq-listed.csv"
    nyse_url = "https://datahub.io/core/nyse-other-listings/_r/-/data/nyse-listed.csv"
    other_url = "https://datahub.io/core/nyse-other-listings/_r/-/data/other-listed.csv"
    
    try:
        # NASDAQ uses 'Symbol' and 'Security Name'
        nasdaq = pd.read_csv(nasdaq_url)
        nasdaq_clean = nasdaq[['Symbol', 'Security Name']].rename(columns={'Symbol': 'Ticker', 'Security Name': 'Name'})
        nasdaq_clean['Exchange'] = 'NASDAQ'
        
        # NYSE and Other use 'ACT Symbol' and 'Company Name'
        nyse = pd.read_csv(nyse_url)
        # Just use these two to be safe
        nyse_clean = nyse[['ACT Symbol', 'Company Name']].rename(columns={'ACT Symbol': 'Ticker', 'Company Name': 'Name'})
        nyse_clean['Exchange'] = 'NYSE'
        
        other = pd.read_csv(other_url)
        other_clean = other[['ACT Symbol', 'Company Name']].rename(columns={'ACT Symbol': 'Ticker', 'Company Name': 'Name'})
        other_clean['Exchange'] = 'OTHER/AMEX'
        
        all_tickers = pd.concat([nasdaq_clean, nyse_clean, other_clean]).drop_duplicates(subset=['Ticker'])
        all_tickers = all_tickers.sort_values('Ticker')
        all_tickers = all_tickers[all_tickers['Ticker'].notna()]
        
        output_path = "c:/Users/Allen/OneDrive/Desktop/tw/My-US-Coverage/tickers_us.csv"
        all_tickers.to_csv(output_path, index=False)
        print(f"Successfully saved {len(all_tickers)} tickers to {output_path}")
        
    except Exception as e:
        print(f"Error fetching tickers: {e}")

if __name__ == "__main__":
    fetch_tickers()
