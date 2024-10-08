import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from openai import OpenAI
import logging
from extract_message import check_user_id, client
from fetch_forex_data import fetch_forex_data
from format_signal import format_signal
from constants import BotMessages 
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from constants import CURRENCY_PAIRS
from get_trading_signal import get_trading_signal
from dotenv import load_dotenv
import os

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)

API_TOKEN = os.environ.get("BOT_API_TOKEN")

# Set maximum allowed test signals
MAX_TEST_SIGNALS = 1

# In-memory dictionary to track test signal usage by each user (could be replaced by database)
user_signal_count = {}
user_verification_data = {}
isTestSignal = False

# Dictionary to track the last time each user accessed the select_pair command
user_last_access_time = {}
COOLDOWN_PERIOD = 10  # Cooldown period in seconds (5 minutes)


# Referral link (replace with your actual link)
REFERRAL_LINK = "https://broker-qx.pro/?lid=1042851"


# Create bot and dispatcher instances
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())



# Command handler for /start with inline buttons
@dp.message(Command(commands=['start']))
async def start(message: types.Message):
    logging.info(f"Start command received from user {message.from_user.id}")
    
    # Create inline keyboard
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🔓 Get access to bot 🤖', callback_data='access_bot')],
        [InlineKeyboardButton(text='📈 Get a test signal 🆓', callback_data='test_signal')],
        [InlineKeyboardButton(text='📞 Contact Hitesh ❓', callback_data='contact_hitesh')]
    ])

    
    # Send start message with inline keyboard
    await message.answer(BotMessages.START_COMMAND_MESSAGE, reply_markup=inline_keyboard)


# Handle inline button callbacks
@dp.callback_query(lambda call: call.data in ['access_bot', 'test_signal', 'contact_hitesh'])
async def handle_inline_buttons(call: types.CallbackQuery):
    user_id = call.from_user.id
    global isTestSignal

    # Test Signal button logic
    if call.data == 'test_signal':
        print('user_signal_count: ', user_signal_count.get(user_id))
        if user_signal_count.get(user_id, 0) < MAX_TEST_SIGNALS:
            # Provide test signal and increment count
            user_signal_count[user_id] = user_signal_count.get(user_id, 0) + 1
            isTestSignal = True
            await select_currency_pair(call.message)
            # await call.message.answer(f"Test signal #{user_signal_count[user_id]}: Your trading signal here...")
        else:
            # Notify user they have exceeded the limit and must sign up
            print('Quota exceeded')
            await send_quota_exceeded_message(call)
    
    elif call.data == 'access_bot':
        await send_signup_message(call)
    
    elif call.data == 'contact_hitesh':
        await call.message.answer(BotMessages.CONTACT_COMMAND_MESSAGE)
        


async def send_signup_message(call: types.CallbackQuery):
    referral_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🔥 Register', url=REFERRAL_LINK)],
        [InlineKeyboardButton(text='✅ I have registered through your link ✅', callback_data='confirm_registration')],
        [InlineKeyboardButton(text='⬅️ Back', callback_data='back_to_menu')]
    ])

    # Using f-string to include the REFERRAL_LINK
    await call.message.answer(
        f"👉 To continue using the bot, register on Quotex via my referral link:\n\n"
        f"⚠️ Use {REFERRAL_LINK} only. Accounts created using other links will not be accepted. "
        "After registration, send your ID here by clicking the button '✅ I registered through your link ✅'.",
        reply_markup=referral_keyboard
    )


# Send the sign-up message when the test signal limit is exceeded
async def send_quota_exceeded_message(call: types.CallbackQuery):
    referral_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🔥 Register', url=REFERRAL_LINK)],
        [InlineKeyboardButton(text='✅ I have registered through your link ✅', callback_data='confirm_registration')],
        [InlineKeyboardButton(text='⬅️ Back', callback_data='back_to_menu')]
    ])

    await call.message.answer(
        "❌ You've already used all your test signals!\n"
        "👉 To continue using the bot, register on Quotex via my referral link:\n\n"
        f"⚠️ Use {REFERRAL_LINK} only. Accounts created using other links will not be accepted. "
        "After registration, send your ID here by clicking the button '✅ I registered through your link ✅'.",
        reply_markup=referral_keyboard
    )


# Handle registration confirmation
# from extract_message import check_user_id  # Import the function from the file where it's defined

@dp.callback_query(lambda call: call.data == 'confirm_registration')
async def confirm_registration(call: types.CallbackQuery):
    user_id = call.from_user.id
    await call.message.answer("Please provide your registration ID for verification.")

    # Register a handler to receive the user's registration ID
    @dp.message()
    async def receive_user_id(message: types.Message):
        user_id_text = message.text.strip()
        print(f"User ID: {user_id_text}")

        # Verify user registration and deposit using the check_user_id function
        try:
            verification_result = await check_user_id(user_id_text)  # Ensure you're passing the correct user ID
            print('verification_result is: ', verification_result)
            if verification_result["status"] == "not_registered":
                await message.answer("User not found. Please register using the provided link.")
            elif verification_result["status"] == "registered" and verification_result["deposit"]:
                # Store user as verified
                user_verification_data[user_id] = True
                await message.answer("Verification successful! You now have full access to the bot.")
            elif verification_result["status"] == "registered" and not verification_result["deposit"]:
                # Not enough deposit
                await message.answer("Please ensure you have a minimum deposit of $50. Then you can access the bot.")
            else:
                # Not enough deposit or not verified
                await message.answer("Verification failed. Please ensure you have a minimum deposit of $50.")
        
        except Exception as e:
            logging.error(f"Error verifying user: {e}")
            await message.answer("An error occurred during verification. Please try again.")

        # Remove the message handler after receiving the user ID
        # dp.message_handlers.unregister(receive_user_id)



# Handle back to menu
@dp.callback_query(lambda call: call.data == 'back_to_menu')
async def back_to_menu(call: types.CallbackQuery):
    await start(call.message)


# Currency pair selection with access control
@dp.message(Command(commands=['select_pair']))
async def select_currency_pair(message: types.Message):
    user_id = message.from_user.id
    current_time = asyncio.get_event_loop().time()  # Get the current time in seconds

    # Check if the user is in cooldown
    last_access_time = user_last_access_time.get(user_id, 0)
    if current_time - last_access_time < COOLDOWN_PERIOD:
        remaining_time = COOLDOWN_PERIOD - (current_time - last_access_time)
        cooldown_message = await message.answer(f"You can only access the currency pair selection every 5 minutes. Please wait {int(remaining_time)} seconds.")
        # Wait for 5 seconds before deleting the message
        await asyncio.sleep(5)
        
        # Delete the cooldown message
        await bot.delete_message(chat_id=message.chat.id, message_id=cooldown_message.message_id)
        return
    
    print(f"User ID: {user_id}")
    print(f"User Signal Count: {user_signal_count.get(user_id, 0)}")
    print(f"Is Test Signal: {isTestSignal}")
    # Check if user is verified
    if user_verification_data.get(user_id, False) or (user_signal_count.get(user_id, 0) < MAX_TEST_SIGNALS and isTestSignal):
        logging.info(f"Selecting currency pair for user {user_id}")
        
        # Create inline buttons for currency pairs, two per row
        buttons = [
            InlineKeyboardButton(text=pair, callback_data=pair) for pair in CURRENCY_PAIRS
        ]
        
        # Group buttons into pairs
        button_pairs = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
        
        # Create a keyboard layout with pairs of buttons
        keyboard = InlineKeyboardMarkup(inline_keyboard=button_pairs)
        
        await message.answer("Please select a currency pair:", reply_markup=keyboard)
        # user_last_access_time[user_id] = current_time
    else:
        await message.answer("You are not verified. Please complete the registration with a minimum deposit of $50 to access this feature.")



# Handle inline button callbacks for trading signals
@dp.callback_query(lambda call: call.data in CURRENCY_PAIRS)
async def handle_currency_pair_selection(call: types.CallbackQuery):
    logging.info(f"Trading signal request received for {call.data} from user {call.from_user.id}")
    current_time = asyncio.get_event_loop().time()  # Get the current time in seconds
    user_id = call.from_user.id
    # Update the last access time for the user after they successfully select a pair
    user_last_access_time[user_id] = current_time
    pair = call.data
    
    # Remove "(OTC)" from the selected pair
    trimmed_pair = pair.replace("(OTC)", "").replace("/", "").strip()
    
    # Acknowledge the callback to hide the buttons
    await call.answer()
    
    # Delete the inline buttons message after selecting the pair
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    
    # Inform the user that we're fetching live data
    loading_message = await bot.send_message(call.from_user.id, f"Fetching live data for {trimmed_pair}. Please wait...")
    
    # Get the trading signal
    signal = await get_trading_signal(trimmed_pair)
    
    # Delete the loading message after fetching the signal
    await bot.delete_message(chat_id=loading_message.chat.id, message_id=loading_message.message_id)
    
    # Send the final trading signal
    await bot.send_message(call.from_user.id, f"{signal}", parse_mode='MarkdownV2')





# Command handler for /help
@dp.message(Command(commands=['help']))
async def help_command(message: types.Message):
    logging.info(f"Help command received from user {message.from_user.id}")
    await message.answer(BotMessages.HELP_COMMAND_MESSAGE)



# Command handler for /contact
@dp.message(Command(commands=['contact']))
async def contact_command(message: types.Message):
    logging.info(f"Contact command received from user {message.from_user.id}")
    await message.answer(BotMessages.CONTACT_COMMAND_MESSAGE)



# Run the bot
async def main():
    logging.info("Starting the bot")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())