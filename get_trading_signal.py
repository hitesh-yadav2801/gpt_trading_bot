import json
from openai import OpenAI
from fetch_forex_data import fetch_forex_data
from format_signal import format_signal
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def load_prompt(file_path):
    """
    Function to load prompt from a file.
    """
    with open(file_path, 'r') as file:
        return file.read()

async def get_trading_signal(pair):
    """
    Function to fetch a trading signal using OpenAI/ChatGPT and live market data.
    """

    prompt_template = load_prompt('prompt.txt')
    # print(prompt_template)
    # Calculate the date for three days ago
    three_days_ago = datetime.now() - timedelta(days=3)
    formatted_date = three_days_ago.strftime('%Y-%m-%d')  # Format the date as 'YYYY-MM-DD'

    # Fetch live Forex data
    from_currency, to_currency = pair[:3], pair[3:]
    market_data = fetch_forex_data(from_currency, to_currency, formatted_date, '5min')

    print(market_data)
    
    # Ensure data was successfully retrieved
    if market_data is not None:
        formatted_prompt = prompt_template.format(pair=pair, market_data=market_data)

        # Using OpenAI to analyze market data and give signal in JSON format
        completion = openai_client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": formatted_prompt},
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
