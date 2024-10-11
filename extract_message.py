import logging
from telethon import TelegramClient, events
import asyncio
import re  # For regex extraction
from dotenv import load_dotenv
import os

load_dotenv()

api_id = os.environ.get('MY_TELEGRAM_API_ID')
api_hash = os.environ.get('MY_TELEGRAM_API_HASH')
bot_username = '@QuotexPartnerBot'  # The username of the Pocket Option bot

# Initialize the Telegram client
client = TelegramClient('session_name', api_id, api_hash)

# Simulated bot response (for testing)
SIMULATE_RESPONSE = False  # Set to False for actual bot interaction
simulated_response_text = (
    "UID: 85614523\n"
    "Reg date: 2024-10-05\n"
    "Activity date: \n"
    "Country: India\n"
    "Verified: No\n"
    "Balance: 0.00\n"
    "FTD amount: $0.00\n"
    "FTD date: \n"
    "Count of deposits: 0\n"
    "Deposits Sum: $ 60.00\n"
    "Sum of bonuses: $0.00\n"
    "Count of bonuses: 0%\n"
    "Commission: $0.00\n"
    "--------------------------\n"
    "Link type: Use a universal Smart-Link\n"
    "Link: https://pocket1.click/smart/QLmdLojLR4E7Et"
)


async def check_user_id(user_id):
    try:
        await client.start()

        # Send the user_id to the bot
        await client.send_message(bot_username, f'{user_id}')

        # Create a future to capture the result
        response_future = asyncio.get_event_loop().create_future()

        if not SIMULATE_RESPONSE:
            # Real bot interaction: event handler for incoming messages
            @client.on(events.NewMessage(chats=bot_username, incoming=True))
            async def handler(event):
                response_text = event.raw_text
                await process_response(response_text, response_future)
                # client.remove_event_handler(handler)
        else:
            # Simulate a bot response (for testing)
            response_text = simulated_response_text
            await process_response(response_text, response_future)

        # Wait for the future to complete with a timeout (e.g., 30 seconds)
        try:
            return await asyncio.wait_for(response_future, timeout=30)
        except asyncio.TimeoutError:
            print("Timeout while waiting for the response.")
            return {"status": "error", "message": "Timeout waiting for response from bot."}

    except Exception as e:
        logging.error(f"Error verifying user: {e}")
        return {"status": "error", "message": str(e)}
    
    # finally:
    #     await client.disconnect()



async def process_response(response_text, response_future):
    print("Processing response text:", response_text)

    # Check if the future is already set to avoid InvalidStateError
    if response_future.done():
        return

    # Check if the user is not found
    if "was not found" in response_text.lower():
        print(response_text)
        response_future.set_result({"status": "not_registered"})
        return

    # Extract the **Deposits Sum** field using regex
    deposit_match = re.search(r"Deposits Sum:\s*\$\s*(\d+\.?\d*)", response_text)
    print(f"Deposit match: {deposit_match}")

    if deposit_match:
        deposit_amount = float(deposit_match.group(1))  # Extracted deposit amount as a float
        print(f"Deposit amount: {deposit_amount}")

        if deposit_amount == 0:
            print("You have no deposits.")
            result = {"status": "registered", "deposit": False}
        elif deposit_amount >= 50:
            print("You have more than $50 deposits.")
            result = {"status": "registered", "deposit": True}
        else:
            print("You have less than $50 deposits.")
            result = {"status": "registered", "deposit": False}
    else:
        print("No deposit information found.")
        result = {"status": "registered", "deposit": False}

    # Ensure the future is set with a result
    if not response_future.done():
        response_future.set_result(result)


# Example usage (commented out, this would be run as part of your program)
# asyncio.run(check_user_id(123456789))
