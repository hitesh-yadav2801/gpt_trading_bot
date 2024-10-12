import ast
import json
import logging
from openai import OpenAI
from fetch_forex_data import fetch_forex_data
from format_signal import format_signal, format_signal_fallback
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)
logging.basicConfig(level=logging.INFO)

def load_prompt(file_path):
    """
    Function to load prompt from a file.
    """
    with open(file_path, 'r') as file:
        return file.read()

def parse_response(response):
    """
    Parse the response from OpenAI, handling both JSON and Python dict-like strings.
    """
    try:
        # First, try to parse as JSON
        return json.loads(response)
    except json.JSONDecodeError:
        try:
            # If JSON fails, try to parse as a Python literal
            print("Parsing as Python literal")
            return ast.literal_eval(response)
        except (ValueError, SyntaxError):
            # If both fail, raise an exception
            raise ValueError("Failed to parse the response")

async def get_trading_signal(pair):
    """
    Function to fetch a trading signal using OpenAI/ChatGPT and live market data.
    """
    try:
        prompt_template = load_prompt('prompt.txt')
        three_days_ago = datetime.now() - timedelta(days=3)
        formatted_date = three_days_ago.strftime('%Y-%m-%d')

        # Fetch live Forex data
        from_currency, to_currency = pair[:3], pair[3:]
        market_data = fetch_forex_data(from_currency, to_currency, formatted_date, '5min')
        
        logging.info(f"Market data for {pair}: {market_data}")
        
        if market_data is not None:
            formatted_prompt = prompt_template.format(pair=pair, market_data=market_data)
            
            completion = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": formatted_prompt},
                    {"role": "user", "content": "What is the trading signal?"}
                ]
            )
            print(completion.choices[0].message)
            response = completion.choices[0].message.content.strip()
            logging.info(f"OpenAI response for {pair}: {response}")
            
            try:
                signal_data = parse_response(response)
                
                formatted_signal = format_signal(
                    pair=pair, 
                    timeframe=5,
                    moving_average=signal_data.get('moving_average', 'N/A'), 
                    technical_indicators=signal_data.get('technical_indicators', 'N/A'), 
                    signal_type=signal_data.get('signal_type', 'N/A')
                )
                
                logging.info(f"Formatted signal for {pair}: {formatted_signal}")
                return formatted_signal
            except ValueError as e:
                logging.error(f"Error parsing OpenAI response: {e}")
                return format_signal_fallback(pair, response)
        else:
            logging.error(f"Failed to retrieve market data for {pair}")
            return "Failed to retrieve market data for analysis."
    except Exception as e:
        logging.error(f"Unexpected error in get_trading_signal: {e}")
        return "An unexpected error occurred while generating the trading signal."