def format_signal(pair, timeframe, moving_average, technical_indicators, signal_type):
    # Trim the pair and insert a `/` between the two currencies
    formatted_pair = f"{pair[:3]}/{pair[3:]}\\(OTC\\)"  # Escaped parentheses

    # Decide the arrow based on the signal type
    if signal_type.lower() in ["strong buy", "buy"]:
        arrow = "⬆️🟢"
    elif signal_type.lower() in ["strong sell", "sell"]:
        arrow = "⬇️🔴"
    else:
        arrow = "⬅️🟡"
    
    # Escape characters for MarkdownV2 formatting
    formatted_pair = formatted_pair.replace('-', '\\-')
    moving_average = moving_average.replace('-', '\\-')
    technical_indicators = technical_indicators.replace('-', '\\-')
    signal_type = signal_type.replace('-', '\\-')

    # Return the formatted message with bold text for important values
    return (
        f"*{formatted_pair}*\n"
        f"Time: *{timeframe} MIN*\n"
        f"Broker: *Quotex*\n\n"
        f"📍 Moving average: *{moving_average}*\n"
        f"📊 Technical indicators: *{technical_indicators}*\n\n"
        f"🤖 Trading signal from bot: *{signal_type.upper()}* {arrow}"
    )
