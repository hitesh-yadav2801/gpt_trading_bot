import asyncio
import random
import logging
from format_signal import format_signal

logging.basicConfig(level=logging.INFO)

# Define possible signal values
possible_signals = {
    "signal_type": ["Buy", "Sell"],
    "moving_average": ["Buy", "Sell"],
    "technical_indicators": ["Buy", "Sell"]
}

# Define probability distribution
signal_probability = {
    "Buy": 0.5,
    "Sell": 0.5
}

def get_random_signal():
    """
    Randomly selects moving average and technical indicators based on defined probabilities.
    Ensures that the signal type is aligned if both indicators are in the same direction.
    """
    moving_average = random.choices(
        possible_signals['moving_average'],
        weights=[signal_probability[s] for s in possible_signals['moving_average']]
    )[0]
    
    technical_indicators = random.choices(
        possible_signals['technical_indicators'],
        weights=[signal_probability[s] for s in possible_signals['technical_indicators']]
    )[0]
    
    # If technical indicator is 'Buy', align moving average and signal_type to 'Buy', and vice versa for 'Sell'
    if technical_indicators == "Buy":
        moving_average = "Buy"
        signal_type = "Buy"
    elif technical_indicators == "Sell":
        moving_average = "Sell"
        signal_type = "Sell"
    
    return {
        "signal_type": signal_type,
        "moving_average": moving_average,
        "technical_indicators": technical_indicators
    }

async def get_demo_trading_signal(pair):
    """
    Function to generate a demo trading signal based on random probabilities.
    """
    try:
        # Generate random signal data
        signal_data = get_random_signal()
        logging.info(f"Generated demo signal for {pair}: {signal_data}")

        # Format the signal
        formatted_signal = format_signal(
            pair=pair,
            timeframe=5,
            moving_average=signal_data.get('moving_average', 'N/A'),
            technical_indicators=signal_data.get('technical_indicators', 'N/A'),
            signal_type=signal_data.get('signal_type', 'N/A')
        )
        
        logging.info(f"Formatted demo signal for {pair}: {formatted_signal}")
        return formatted_signal
    
    except Exception as e:
        logging.error(f"Unexpected error in get_demo_trading_signal: {e}")
        return "An unexpected error occurred while generating the demo trading signal."

# Example usage
async def main():
    pair = "EURUSD"
    demo_signal = await get_demo_trading_signal(pair)
    print(demo_signal)

if __name__ == "__main__":
    asyncio.run(main())


# import asyncio
# import random
# import logging
# from format_signal import format_signal

# logging.basicConfig(level=logging.INFO)

# # Define possible signal values
# possible_signals = {
#     "signal_type": ["Buy", "Strong Buy", "Sell", "Strong Sell", "Neutral"],
#     "moving_average": ["Buy", "Strong Buy", "Sell", "Strong Sell", "Neutral"],
#     "technical_indicators": ["Buy", "Strong Buy", "Sell", "Strong Sell", "Neutral"]
# }

# # Define probability distribution
# signal_probability = {
#     "Buy": 0.35, "Strong Buy": 0.1,
#     "Sell": 0.35, "Strong Sell": 0.1,
#     "Neutral": 0.1
# }

# def get_random_signal():
#     """
#     Randomly selects moving average and technical indicators based on defined probabilities.
#     Ensures that the signal type is aligned if both indicators are in the same direction.
#     """
#     moving_average = random.choices(
#         possible_signals['moving_average'],
#         weights=[signal_probability[s] for s in possible_signals['moving_average']]
#     )[0]
    
#     technical_indicators = random.choices(
#         possible_signals['technical_indicators'],
#         weights=[signal_probability[s] for s in possible_signals['technical_indicators']]
#     )[0]
    
#     # Determine signal_type based on the alignment of moving_average and technical_indicators
#     if moving_average == technical_indicators:
#         signal_type = moving_average  # Align the signal type if both are the same
#     else:
#         # If they are different, follow a stronger side approach or choose one randomly
#         if "Strong" in moving_average:
#             signal_type = moving_average  # Prioritize Strong Buy/Sell
#         elif "Strong" in technical_indicators:
#             signal_type = technical_indicators
#         else:
#             # If no Strong signals, choose one randomly
#             signal_type = random.choice([moving_average, technical_indicators])
    
#     return {
#         "signal_type": signal_type,
#         "moving_average": moving_average,
#         "technical_indicators": technical_indicators
#     }

# async def get_demo_trading_signal(pair):
#     """
#     Function to generate a demo trading signal based on random probabilities.
#     """
#     try:
#         # Generate random signal data
#         signal_data = get_random_signal()
#         logging.info(f"Generated demo signal for {pair}: {signal_data}")

#         # Format the signal
#         formatted_signal = format_signal(
#             pair=pair,
#             timeframe=5,
#             moving_average=signal_data.get('moving_average', 'N/A'),
#             technical_indicators=signal_data.get('technical_indicators', 'N/A'),
#             signal_type=signal_data.get('signal_type', 'N/A')
#         )
        
#         logging.info(f"Formatted demo signal for {pair}: {formatted_signal}")
#         return formatted_signal
    
#     except Exception as e:
#         logging.error(f"Unexpected error in get_demo_trading_signal: {e}")
#         return "An unexpected error occurred while generating the demo trading signal."

# # Example usage
# async def main():
#     pair = "EURUSD"
#     demo_signal = await get_demo_trading_signal(pair)
#     print(demo_signal)

# if __name__ == "__main__":
#     asyncio.run(main())
