import requests
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

Tiingo_API_Key = os.environ.get('TIINGO_API_KEY')

def fetch_forex_data(from_currency, to_currency, start_date, resample_freq):
    # Define the headers for the request
    headers = {
        'Content-Type': 'application/json'
    }

    # Construct the parameters for the request
    params = {
        "tickers": f"{from_currency}{to_currency}",
        "startDate": start_date,
        "resampleFreq": resample_freq,
        "token": Tiingo_API_Key  # Use your actual API key
    }

    # Define the base URL
    url = "https://api.tiingo.com/tiingo/fx/prices"

    # Send a GET request to the Tiingo API with parameters
    response = requests.get(url, headers=headers, params=params)

    # Check if the response is successful
    if response.status_code == 200:
        data = response.json()

        # Create a DataFrame from the response data
        df = pd.DataFrame.from_dict(data)
        if len(df) > 100:
            df = df.tail(100)
        
        # Optionally print the first 3 entries for inspection
        # pprint(data[:3])
        # csv_filename = f"{from_currency}_{to_currency}_{start_date}_{resample_freq}.csv"
        # df.to_csv(csv_filename, index=False)

        # Return the DataFrame
        return df
    else:
        print(f"Failed to fetch data: {response.status_code}")
        print(response.text)
        return None

# Example usage: call the function and get the data
# forex_data = fetch_and_save_forex_data('EUR', 'USD', '2024-10-04', '5min')

# # Check and print the fetched DataFrame
# if forex_data is not None:
#     print(forex_data.head())  # Print the first few rows
# else:
#     print("No data fetched.")
