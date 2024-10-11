import logging
from telethon import TelegramClient, events
import asyncio
import re
from dotenv import load_dotenv
import os
from collections import deque

load_dotenv()

api_id = os.environ.get('MY_TELEGRAM_API_ID')
api_hash = os.environ.get('MY_TELEGRAM_API_HASH')
bot_username = '@QuotexPartnerBot'

client = TelegramClient('session_name', api_id, api_hash)

# Queue to manage concurrent requests
request_queue = deque()

# Dictionary to store user-specific futures
user_futures = {}

async def process_queue():
    while True:
        if request_queue:
            user_id, telegram_user_id = request_queue.popleft()
            await process_user_request(user_id, telegram_user_id)
        await asyncio.sleep(1)  

async def process_user_request(user_id, telegram_user_id):
    try:
        # Send the user_id to the bot
        await client.send_message(bot_username, f'{user_id}')
        print('Message sent to bot.')
        # Wait for the response with a timeout
        try:
            response = await asyncio.wait_for(user_futures[telegram_user_id], timeout=30)
            print('The response is:', response)
            result = await process_response(response)
            print('The result is:', result)
        except asyncio.TimeoutError:
            result = {"status": "error", "message": "Timeout waiting for response from bot."}
        
        # Set the result in the future
        user_futures[telegram_user_id].set_result(result)
        print('The future is:', user_futures[telegram_user_id])
    except Exception as e:
        logging.error(f"Error processing request for user {telegram_user_id}: {e}")
        user_futures[telegram_user_id].set_exception(e)
    finally:
        # Clean up the future
        del user_futures[telegram_user_id]

async def check_user_id(user_id, telegram_user_id):
    try:
        # Create a future for this specific user
        user_futures[telegram_user_id] = asyncio.get_event_loop().create_future()
        
        # Add the request to the queue
        request_queue.append((user_id, telegram_user_id))
        
        # Wait for the result
        return await user_futures[telegram_user_id]
    except Exception as e:
        logging.error(f"Error checking user ID: {e}")
        return {"status": "error", "message": str(e)}

async def process_response(response_text):
    print("Processing response text:", response_text)
    if "was not found" in response_text.lower():
        return {"status": "not_registered"}

    deposit_match = re.search(r"Deposits Sum:\s*\$\s*([\d,]+\.\d+)", response_text)
    if deposit_match:
        deposit_amount = float(deposit_match.group(1).replace(',', ''))
        if deposit_amount == 0:
            return {"status": "registered", "deposit": False}
        elif deposit_amount >= 50:
            return {"status": "registered", "deposit": True}
        else:
            return {"status": "registered", "deposit": False}
    else:
        return {"status": "registered", "deposit": False}

@client.on(events.NewMessage(chats=bot_username, incoming=True))
async def handler(event):
    # Find the corresponding user future and set the result
    for telegram_user_id, future in user_futures.items():
        if not future.done():
            future.set_result(event.raw_text)
            break

async def main():
    await client.start()
    print('Client started...')
    # Start the queue processing task
    asyncio.create_task(process_queue())
    print('Queue processing task started...')
    # await check_user_id(49775259, 793076295)
    # Run the client
    await client.run_until_disconnected()
    print('Client disconnected...')

if __name__ == "__main__":
    asyncio.run(main())