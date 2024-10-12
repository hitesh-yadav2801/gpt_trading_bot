import re
import logging

def escape_markdown_v2(text):
    """
    Escape special characters for Telegram's MarkdownV2 format.
    """
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', str(text))

def format_signal(pair, timeframe, moving_average, technical_indicators, signal_type):
    """
    Format the trading signal with proper MarkdownV2 escaping.
    """
    try:
        formatted_pair = f"{pair[:3]}/{pair[3:]}(OTC)"

        if signal_type.lower() in ["strong buy", "buy"]:
            arrow = "⬆️🟢"
        elif signal_type.lower() in ["strong sell", "sell"]:
            arrow = "⬇️🔴"
        else:
            arrow = "⬅️🟡"
        
        # Escape all strings for MarkdownV2 formatting
        formatted_pair = escape_markdown_v2(formatted_pair)
        timeframe = escape_markdown_v2(timeframe)
        moving_average = escape_markdown_v2(moving_average)
        technical_indicators = escape_markdown_v2(technical_indicators)
        signal_type = escape_markdown_v2(signal_type)

        return (
            f"*{formatted_pair}*\n"
            f"Time: *{timeframe} MIN*\n"
            f"Broker: *Quotex*\n\n"
            f"📍 Moving average: *{moving_average}*\n"
            f"📊 Technical indicators: *{technical_indicators}*\n\n"
            f"🤖 Trading signal from bot: *{signal_type.upper()}* {arrow}"
        )
    except Exception as e:
        logging.error(f"Error in format_signal: {e}")
        return format_signal_fallback(pair, f"{moving_average}, {technical_indicators}, {signal_type}")

def format_signal_fallback(pair, raw_signal):
    """
    Fallback formatting function in case the main formatting fails.
    """
    formatted_pair = escape_markdown_v2(f"{pair[:3]}/{pair[3:]}(OTC)")
    escaped_signal = escape_markdown_v2(raw_signal)
    return f"*{formatted_pair}*\n\nSignal: {escaped_signal}"