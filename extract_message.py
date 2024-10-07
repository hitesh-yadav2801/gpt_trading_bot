import logging
from telethon import TelegramClient, events
import asyncio
import re  # We'll use regex to extract deposit amounts

api_id = '20657390'
api_hash = '39a41e259c349930c1898ce919a67397'
bot_username = '@AffiliatePocketBot'  # The username of the Pocket Option bot

# Initialize the Telegram client
client = TelegramClient('session_name', api_id, api_hash)

async def check_user_id(user_id):
    try:
        await client.start()

        # Send the user ID to the affiliate bot
        await client.send_message(bot_username, f'/{user_id}')

        # Create a future to capture the result
        response_future = asyncio.get_event_loop().create_future()

        # Event handler for incoming messages
        @client.on(events.NewMessage(chats=bot_username, incoming=True))
        async def handler(event):
            response_text = event.raw_text
            print("Raw response text:", response_text)

            # Simulated bot response for testing
            # response_text = """UID: 85614523
            #     Reg date: 2024-10-05
            #     Activity date: 
            #     Country: India
            #     Verified: No
            #     Balance: 0.00
            #     FTD amount: $0.00
            #     FTD date: 
            #     Count of deposits: 0
            #     Sum of deposits: $50.00
            #     Sum of bonuses: $0.00
            #     Count of bonuses: 0%
            #     Commission: $0.00
            #     --------------------------
            #     Link type: Use a universal Smart-Link
            #     Link: https://pocket1.click/smart/QLmdLojLR4E7Et"""

            # Check if the user is not found
            if "user not found" in response_text.lower():
                response_future.set_result({"status": "not_registered"})
                client.remove_event_handler(handler)
                return

            # Extract the **Sum of deposits** field using regex
            deposit_match = re.search(r"Sum of deposits:\s*\$(\d+\.?\d*)", response_text)
            print(f"Deposit match: {deposit_match}")

            result = None
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

            # Set the result for the future
            response_future.set_result(result)
            client.remove_event_handler(handler)

        # Wait for the future to complete (or timeout)
        await asyncio.wait_for(response_future, timeout=10)
        return response_future.result()

    except asyncio.TimeoutError:
        print("Timeout while waiting for the response.")
        return {"status": "error", "message": "Timeout waiting for response from bot."}

    except Exception as e:
        logging.error(f"Error verifying user: {e}")
        return {"status": "error", "message": str(e)}


# Example usage: checking a specific user ID
# user_id_to_check = 85614523  # Replace this with the user ID you want to check

# if __name__ == '__main__':
#     asyncio.run(check_user_id(user_id_to_check))
