from telethon import TelegramClient, events
import asyncio
import re  # We'll use regex to extract deposit amounts

api_id = '20657390'
api_hash = '39a41e259c349930c1898ce919a67397'
bot_username = '@AffiliatePocketBot'  # The username of the Pocket Option bot

# Initialize the Telegram client
client = TelegramClient('session_name', api_id, api_hash)

async def check_user_id(user_id):
    await client.start()

    # Send the user ID to the affiliate bot
    await client.send_message(bot_username, str(f'/{user_id}'))

    # Wait for the response from the bot
    @client.on(events.NewMessage(chats=bot_username, incoming=True))
    async def handler(event):
        response_text = event.raw_text
        print(type(response_text))

        # Check if the user is not found
        if "user not found" in response_text.lower():
            return {"status": "not_registered"}
        
        # Extract deposit amount using regex (assuming response contains "Deposit: $XX")
        deposit_match = re.search(r"Deposit:\s*\$(\d+)", response_text)
        print(deposit_match)
        
        if deposit_match:
            deposit_amount = int(deposit_match.group(1))  # Extracted deposit amount
            print(f"Deposit amount: {deposit_amount}")  # This is only executed when a deposit is found
            if deposit_amount >= 50:
                return {"status": "registered", "deposit": True}
            else:
                return {"status": "registered", "deposit": False}
        else:
            # No deposit information found in response
            print("No deposit information found.")
            return {"status": "registered", "deposit": False}

    # Allow time for bot response
    await asyncio.sleep(2)

    # Unregister handler
    client.remove_event_handler(handler)


# Example usage: checking a specific user ID
user_id_to_check = 85614523  # Replace this with the user ID you want to check
with client:
    client.loop.run_until_complete(check_user_id(user_id_to_check))
