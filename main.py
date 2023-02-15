import telebot

API_TOKEN = '6267872736:AAFif1GKVPKThRpBTqNqnqvX8RObPwKudN4'
shop_bot = telebot.TeleBot(API_TOKEN)

# telebot.types.ReplyKeyboardMarkup
# telebot.types.InlineKeyboardMarkup

commands = ['Add to list', 'Get list', 'Remove from list']
keyboard = telebot.types.ReplyKeyboardMarkup()
keyboard.row(*commands)


shopping_list = []
current_operation = None
last_message_id = None


@shop_bot.message_handler(commands=['start'])
def start(message):
    shop_bot.reply_to(message, 'Welcome to shopping bot', reply_markup=keyboard)


@shop_bot.message_handler(content_types=['text'])
def command(message):
    global current_operation
    global shopping_list
    global last_message_id
    if message.text == 'Add to list':
        current_operation = 'add'
        shop_bot.reply_to(message, 'Add items to the list')
    elif message.text == 'Get from list':
        current_operation = 'get'
        shop_bot.reply_to(message, ', '.join(shopping_list) if shopping_list else 'Your list is empty')
    elif message.text == 'Remove from list':
        current_operation = 'rm'
        inline_kb = telebot.types.InlineKeyboardMarkup()
        for elem in shopping_list:
            inline_kb.add(telebot.types.InlineKeyboardButton(elem, callback_data=elem))
        res = shop_bot.reply_to(message, 'Now you can delete item', reply_markup=inline_kb)
        last_message_id = res.message_id
    else:
        if current_operation == 'add':
            shopping_list.append(message.text)
            shop_bot.reply_to(message, f'successfully add {message.text}')


@shop_bot.callback_query_handler(func=lambda x:True)
def callback_handler(call):
    global shopping_list
    if call.data in shopping_list:
        shopping_list.remove(call.data)

    inline_kb = telebot.types.InlineKeyboardMarkup()
    for elem in shopping_list:
        inline_kb.add(telebot.types.InlineKeyboardButton(elem, callback_data=elem))
    shop_bot.edit_message_reply_markup(call.message.chat.id, last_message_id, reply_markup=inline_kb)


shop_bot.polling()
