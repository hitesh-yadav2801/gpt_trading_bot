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
        await asyncio.sleep(10)  

async def process_user_request(user_id, telegram_user_id):
    try:
        # Send the user_id to the bot
        await client.send_message(bot_username, f'{user_id}')
        print('Message sent to bot.')
        # Wait for the response with a timeout
        try:
            response = await asyncio.wait_for(user_futures[telegram_user_id], timeout=30)
            print('The response is:', response)
            # result = await process_response(response)
            # print('The result is:', result)
        except asyncio.TimeoutError:
            response = {"status": "error", "message": "Timeout waiting for response from bot."}
        
        # Set the result in the future if it's not already done
        if telegram_user_id in user_futures and not user_futures[telegram_user_id].done():
            print("Setting the future result")
            user_futures[telegram_user_id].set_result(response)
        print('The future result is:', user_futures[telegram_user_id].result())
    except Exception as e:
        logging.error(f"Error processing request for user {telegram_user_id}: {e}")
        if telegram_user_id in user_futures and not user_futures[telegram_user_id].done():
            user_futures[telegram_user_id].set_exception(e)
    finally:
        # Clean up the future
        user_futures.pop(telegram_user_id, None)

async def check_user_id(user_id, telegram_user_id):
    try:
        if not client.is_connected():
            await client.start()
            print('Client started...')
            # Start the queue processing task
            queue_task = asyncio.create_task(process_queue())
            print('Queue processing task started...')
        # Create a future for this specific user
        user_futures[telegram_user_id] = asyncio.get_event_loop().create_future()
        
        # Add the request to the queue
        request_queue.append((user_id, telegram_user_id))
        
        # Wait for the result
        future_result = await user_futures[telegram_user_id]
        print('final future result:', future_result)
        return future_result
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
            processed_result = await process_response(event.raw_text)
            print(f"Processed result for user ID {telegram_user_id}: {processed_result}")
            future.set_result(processed_result)
            break


async def main():
    await client.start()
    print('Client started...')
    # Start the queue processing task
    queue_task = asyncio.create_task(process_queue())
    print('Queue processing task started...')
    
    try:
        for i in range(1):
            a = 1211313 + i
            b = 49775259 + i
            result = await check_user_id(a, b)
            print(f'Check result for user ID {a}: {result}')
            await asyncio.sleep(1)
    finally:
        # Cancel the queue processing task
        queue_task.cancel()
        try:
            await queue_task
        except asyncio.CancelledError:
            pass
        print('Queue processing task cancelled')
    
    # Run the client
    await client.run_until_disconnected()
    print('Client disconnected...')

if __name__ == "__main__":
    print('Starting the bot...')
    asyncio.run(main())
    print('Bot stopped...')