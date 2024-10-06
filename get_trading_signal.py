# Async function to get trading signal
import json
from openai import OpenAI
from fetch_forex_data import fetch_and_save_forex_data
from format_signal import format_signal


OPENAI_API_KEY = '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'

# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

async def get_trading_signal(pair):
    """
    Function to fetch a trading signal using OpenAI/ChatGPT and live market data.
    """
    # Fetch live Forex data
    from_currency, to_currency = pair[:3], pair[3:]
    market_data = fetch_and_save_forex_data(from_currency, to_currency, '2024-10-01', '5min')

    print(market_data)
    
    # Ensure data was successfully retrieved
    if market_data is not None:
        # Using OpenAI to analyze market data and give signal in JSON format
        completion = openai_client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": f"Analyze the following market data for {pair} and provide a JSON object with the keys: 'signal_type', 'moving_average', and 'technical_indicators'. For example: {{'signal_type': 'Buy', 'moving_average': 'Neutral', 'technical_indicators': 'Sell'}}. Here is the data: {market_data}. Don't give unnecessary information. Just provide the JSON object."},
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
