import json
from openai import OpenAI
from fetch_forex_data import fetch_forex_data
from format_signal import format_signal
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
# OPENAI_API_KEY = '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'

# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

async def get_trading_signal(pair):
    """
    Function to fetch a trading signal using OpenAI/ChatGPT and live market data.
    """
    # Calculate the date for three days ago
    three_days_ago = datetime.now() - timedelta(days=3)
    formatted_date = three_days_ago.strftime('%Y-%m-%d')  # Format the date as 'YYYY-MM-DD'

    # Fetch live Forex data
    from_currency, to_currency = pair[:3], pair[3:]
    market_data = fetch_forex_data(from_currency, to_currency, formatted_date, '5min')

    print(market_data)
    
    # Ensure data was successfully retrieved
    if market_data is not None:
        # Using OpenAI to analyze market data and give signal in JSON format
        completion = openai_client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": f"Analyze the following market data for {pair} and provide a JSON object with the keys: 'signal_type', 'moving_average', and 'technical_indicators'. For example: {{'signal_type': 'Buy', 'moving_average': 'Neutral', 'technical_indicators': 'Sell'}}. If market potential is high then use Strong Buy or Buy. If market potential is low then use Strong Sell or Sell. Here is the data: {market_data}. Don't give unnecessary information. Just provide the JSON object."},
                {"role": "user", "content": "What is the trading signal?"}
            ]
        )
        
        # Get the response from OpenAI
        response = completion.choices[0].message.content.strip()
        print('Response is:', response)

        try:
            # Parse the JSON response
            signal_data = json.loads(response)

            # Call format_signal to return the formatted signal
            formatted_signal = format_signal(
                pair=pair, 
                timeframe=5,  # Assuming 5 min is used, you can dynamically update this
                moving_average=signal_data['moving_average'], 
                technical_indicators=signal_data['technical_indicators'], 
                signal_type=signal_data['signal_type']
            )
            
            print('Formatted signal is:', formatted_signal)
            return formatted_signal
        except ValueError:
            return "Failed to parse signal from GPT response."
    else:
        return "Failed to retrieve market data for analysis."
