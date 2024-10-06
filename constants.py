# constants.py

class BotMessages:
    MY_USERNAME = "@noah_2_8"

    START_COMMAND_MESSAGE = (
        "👋🤖 Hi, are you ready to get a unique trading robot based on artificial "
        "intelligence in conjunction with 15 indicators?\n\n"
        "🏆 I want to tell you right away that this is not gold bars that will come "
        "to your hands by themselves.\n\n"
        "This is a shovel that you can use to dig out your gold!\n\n"
        "✅ Trading is a path you have to take yourself! And this bot will help you "
        "to do it! I spent a lot of money and time to make this bot free for everyone. "
        "You need to follow some simple steps to get started, it will take you 10 minutes.\n\n"
        "Click the \"Get access to bot\" button and you'll get instructions to get started!"
    )

    HELP_COMMAND_MESSAGE = (
    "🤖 Need guidance on your trading journey? I'm here to help! 🚀\n\n"
    "👇 Here's how you can get started with our trading bot:\n"
    "🔹 Use /select_pair to choose your preferred currency pair 📈\n"
    "🔸 Tap /start to embark on your trading adventure 🌟\n"
    "🔹 Use /help any time you're seeking more guidance 🛠️\n"
    "🔸 Reach out with /contact if you have questions or need support 💬\n\n"
    "Let's make your trading experience smooth and successful! 💼"
    )

    CONTACT_COMMAND_MESSAGE = (
    "📣 Have questions or looking to take your trading to the next level? 🏆\n\n"
    "🔑 Unlock exclusive insights in my PRIVATE channel, where I personally provide trading signals! 📊\n\n"
    "💬 Feel free to message me directly at {MY_USERNAME} and get started on your trading journey today! 🚀"
    )



BotMessages.CONTACT_COMMAND_MESSAGE = BotMessages.CONTACT_COMMAND_MESSAGE.format(MY_USERNAME=BotMessages.MY_USERNAME)

