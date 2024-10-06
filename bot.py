import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from openai import OpenAI
import logging
from fetch_forex_data import fetch_and_save_forex_data
from format_signal import format_signal
from constants import BotMessages 
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from get_trading_signal import get_trading_signal

# Set up logging
logging.basicConfig(level=logging.INFO)

API_TOKEN = '7487400596:AAHuNmLoSN3mNo7IbShJNsr0It3Hq1xGBfg'

# Set maximum allowed test signals
MAX_TEST_SIGNALS = 1

# In-memory dictionary to track test signal usage by each user (could be replaced by database)
user_signal_count = {}

# Referral link (replace with your actual link)
REFERRAL_LINK = "https://pocket1.click/smart/QLmdLojLR4E7Et"


# Create bot and dispatcher instances
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())



# Currency pairs list
CURRENCY_PAIRS = [
    'USD/JPY(OTC)', 'EUR/GBP(OTC)', 'EUR/JPY(OTC)', 'AUD/JPY(OTC)',
    'EUR/USD(OTC)', 'GBP/USD(OTC)', 'GBP/CHF(OTC)', 'EUR/CAD(OTC)', 
    'AUD/USD(OTC)', 'USD/CAD(OTC)', 'GBP/CAD(OTC)', 'EUR/CHF(OTC)', 
    'AUD/CHF(OTC)', 'AUD/CAD(OTC)'
]


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

    # Test Signal button logic
    if call.data == 'test_signal':
        if user_signal_count.get(user_id, 0) < MAX_TEST_SIGNALS:
            # Provide test signal and increment count
            user_signal_count[user_id] = user_signal_count.get(user_id, 0) + 1
            await call.message.answer(f"Test signal #{user_signal_count[user_id]}: Your trading signal here...")
        else:
            # Notify user they have exceeded the limit and must sign up
            await send_quota_exceeded_message(call)
    
    elif call.data == 'access_bot':
        await send_signup_message(call)
    
    elif call.data == 'contact_hitesh':
        await call.message.answer("You can contact Hitesh via this Telegram: @hitesh...")


async def send_signup_message(call: types.CallbackQuery):
    referral_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🔥 Register', url=REFERRAL_LINK)],
        [InlineKeyboardButton(text='✅ I have registered through your link ✅', callback_data='confirm_registration')],
        [InlineKeyboardButton(text='⬅️ Back', callback_data='back_to_menu')]
    ])

    # Using f-string to include the REFERRAL_LINK
    await call.message.answer(
        f"👉 To continue using the bot, register on Pocket Option via my referral link:\n\n"
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
        "👉 To continue using the bot, register on Pocket Option via my referral link:\n\n"
        "⚠️ Use **this link** only. Accounts created using other links will not be accepted. "
        "After registration, send your ID here by clicking the button '✅ I registered through your link ✅'.",
        reply_markup=referral_keyboard
    )


# Handle registration confirmation
@dp.callback_query(lambda call: call.data == 'confirm_registration')
async def confirm_registration(call: types.CallbackQuery):
    await call.message.answer(
        "Please provide your registration ID for verification. "
        "The bot will verify your registration and give you access."
    )


# Handle back to menu
@dp.callback_query(lambda call: call.data == 'back_to_menu')
async def back_to_menu(call: types.CallbackQuery):
    await start(call.message)


# Currency pair selection with inline buttons
@dp.message(Command(commands=['select_pair']))
async def select_currency_pair(message: types.Message):
    logging.info(f"Selecting currency pair for user {message.from_user.id}")
    
    # Create inline buttons for currency pairs, two per row
    buttons = [
        InlineKeyboardButton(text=pair, callback_data=pair) for pair in CURRENCY_PAIRS
    ]
    
    # Group buttons into pairs
    button_pairs = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    
    # Create a keyboard layout with pairs of buttons
    keyboard = InlineKeyboardMarkup(inline_keyboard=button_pairs)
    
    await message.answer("Please select a currency pair:", reply_markup=keyboard)





# Handle inline button callbacks for trading signals
@dp.callback_query(lambda call: call.data in CURRENCY_PAIRS)
async def handle_currency_pair_selection(call: types.CallbackQuery):
    logging.info(f"Trading signal request received for {call.data} from user {call.from_user.id}")
    
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