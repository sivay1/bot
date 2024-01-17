import requests
from decouple import config
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler


TOKEN = config('TOKEN')
ETHPLORER_API_KEY = config('ETHPLORER_API_KEY')

def start(update: Update, context: CallbackContext) -> None:
    #Function to handle /start command
    update.message.reply_text('Hello! I am your simple token info bot. Send me a token address, and I will provide information about that token.')
    
    
    buttons = [
        [
            InlineKeyboardButton("Buy", callback_data='button1'),
            InlineKeyboardButton("Sell", callback_data='button2'),
        ],
        [
            InlineKeyboardButton("Wallet", callback_data='button3'),
            InlineKeyboardButton("Config", callback_data='button4'),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)

    # Send the message with the inline keyboard
    update.message.reply_text("Choose an option:", reply_markup=reply_markup)

def button_callback(update: Update, context: CallbackContext) -> None:
    #Function to handle button clicks
    query = update.callback_query
    data = query.data

    # Handle different button presses based on the callback data
    if data == 'button1':
        query.edit_message_text(text="You pressed Buy")
    elif data == 'button2':
        query.edit_message_text(text="You pressed Sell")
    elif data == 'button3':
        query.edit_message_text(text="You pressed Wallet")
    elif data == 'button4':
        query.edit_message_text(text="You pressed Config")


def get_token_info(update: Update, context: CallbackContext) -> None:
    #Function to fetch token info and logic
    token_address = update.message.text.strip()
    if token_address.lower() == 'bye':
        return update.message.reply_text('See you next time!')
    
    ethplorer_url = f'https://api.ethplorer.io/getTokenInfo/{token_address}?apiKey={ETHPLORER_API_KEY}'

    try:
        response = requests.get(ethplorer_url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

        if response.status_code == 200:
            token_info = response.json()
            if 'error' in token_info:
                update.message.reply_text(f"Error: {token_info['error']['message']}")
            else:
                decimals = int(token_info['decimals'])
                total_supply = int(token_info['totalSupply']) / 10**decimals
                update.message.reply_text(f"Token Name: {token_info['name']}\nSymbol: {token_info['symbol']}\nTotal Supply: {total_supply}\nDecimals: {token_info['decimals']}")
        
    # except requests.exceptions.HTTPError as http_err:
    #     update.message.reply_text(f"HTTP Error: {http_err}")

    # except requests.exceptions.RequestException as req_err:
    #     update.message.reply_text(f"Request Error: {req_err}")
    except Exception as err:
        update.message.reply_text("An unexpected error occurred: ")

def main() -> None:
    #Main function to start the bot
    updater = Updater(TOKEN)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, get_token_info))
    dp.add_handler(CallbackQueryHandler(button_callback))
    print("Code is now running. Press Ctrl+C to stop.")
    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()

