import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
import logging
from extract_message import check_user_id
from constants import BotMessages 
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from constants import CURRENCY_PAIRS
from get_trading_signal import get_trading_signal
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv
import os
from keep_alive import keep_alive


# keep_alive()
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)

API_TOKEN = os.environ.get("BOT_API_TOKEN")

# MongoDB Setup
# mongo_client = AsyncIOMotorClient("mongodb://localhost:27017/trading_bot")
mongo_client = AsyncIOMotorClient(os.getenv("MONGO_DB_URL"), tlsAllowInvalidCertificates=True)
db = mongo_client["trading_bot"]
users_collection = db["trading_bot_users"]

# Set maximum allowed test signals
MAX_TEST_SIGNALS = 1

# In-memory dictionary to track test signal usage by each user (could be replaced by database)
# user_signal_count = {}
# user_verification_data = {}
isTestSignal = False

# Dictionary to track the last time each user accessed the select_pair command
user_last_access_time = {}
COOLDOWN_PERIOD = 300  # Cooldown period in seconds (5 minutes)


# Referral link (replace with your actual link)
REFERRAL_LINK = "https://broker-qx.pro/?lid=1042851"


# Create bot and dispatcher instances
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())



# Command handler for /start with inline buttons
@dp.message(Command(commands=['start']))
async def start(message: types.Message):
    user_id = message.from_user.id
    print(f"My User ID: {user_id}")
    logging.info(f"Start command received from user {user_id}")
    
    # Check if the user exists in the database
    user = await users_collection.find_one({"telegram_id": user_id})
    
    # If the user doesn't exist, add them to the database
    if not user:
        try:
            await users_collection.insert_one({
                "telegram_id": user_id,
                "user_signal_count": 0,
                "is_registered": False,
                "has_deposited": False
            })
            logging.info(f"User {user_id} added to the database.")
        except PyMongoError as e:
            logging.error(f"Error adding user to the database: {e}")
            await message.answer("An error occurred while processing your request. Please try again later.")
            return
    
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
        user = await users_collection.find_one({"telegram_id": user_id})
        if user and user.get('user_signal_count', 0) <= MAX_TEST_SIGNALS:
            # Provide test signal and increment count
            await users_collection.update_one(
                {"telegram_id": user_id},
                {"$inc": {"user_signal_count": 1}}
            )
            isTestSignal = True
            # print('user id is : ', call.message.from_user.id)
            print('user id is : ', call.message.from_user.id)
            await select_currency_pair(call.message, user_id)
        else:
            # Notify user they have exceeded the limit and must sign up
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

    @dp.message()
    async def receive_user_id(message: types.Message):
        user_id_text = message.text.strip()
        print(f"User ID: {user_id_text}")

        try:
            verification_result = await check_user_id(user_id_text)
            if verification_result["status"] == "not_registered":
                await message.answer("User not found. Please register using the provided link.")
            elif verification_result["status"] == "registered" and verification_result["deposit"]:
                await users_collection.update_one(
                    {"telegram_id": user_id},
                    {"$set": {"is_registered": True, "has_deposited": True}},
                    upsert=True
                )
                await message.answer("Verification successful! You now have full access to the bot.")
            elif verification_result["status"] == "registered" and not verification_result["deposit"]:
                await users_collection.update_one(
                    {"telegram_id": user_id},
                    {"$set": {"is_registered": True, "has_deposited": False}},
                    upsert=True
                )
                await message.answer("Please ensure you have a minimum deposit of $50 and again check with your ID. Then you can access the bot.")
            else:
                await message.answer("Verification failed. Please ensure you have a minimum deposit of $50.")
        
        except Exception as e:
            logging.error(f"Error verifying user: {e}")
            await message.answer("An error occurred during verification. Please try again.")



# Handle back to menu
@dp.callback_query(lambda call: call.data == 'back_to_menu')
async def back_to_menu(call: types.CallbackQuery):
    await start(call.message)


# Currency pair selection with access control
@dp.message(Command(commands=['select_pair']))
async def select_currency_pair(message: types.Message, user_id: int = None):
    if user_id is None:
        user_id = message.from_user.id  # Get user_id from the message if not provided

    current_time = asyncio.get_event_loop().time()  # Get the current time in seconds

    # Check if the user is in cooldown
    last_access_time = user_last_access_time.get(user_id, 0)
    if current_time - last_access_time < COOLDOWN_PERIOD:
        remaining_time = COOLDOWN_PERIOD - (current_time - last_access_time)
        cooldown_message = await message.answer(f"You can only access the currency pair selection every 5 minutes. Please wait {int(remaining_time)} seconds.")
        await asyncio.sleep(5)
        await bot.delete_message(chat_id=message.chat.id, message_id=cooldown_message.message_id)
        return

    user = await users_collection.find_one({"telegram_id": user_id})
    print('user type: ', type(user))
    print('user details: ', user)

    if user and ((user.get("is_registered") and user.get("has_deposited")) or (user.get("user_signal_count", 0) <= MAX_TEST_SIGNALS and isTestSignal)):
        logging.info(f"Selecting currency pair for user {user_id}")

        # Create inline buttons for currency pairs, two per row
        buttons = [
            InlineKeyboardButton(text=pair, callback_data=pair) for pair in CURRENCY_PAIRS
        ]

        # Group buttons into pairs
        button_pairs = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]

        keyboard = InlineKeyboardMarkup(inline_keyboard=button_pairs)
        await message.answer("Please select a currency pair:", reply_markup=keyboard)
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