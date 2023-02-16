import telebot
import flask
import time

app = flask.Flask(__name__)

API_TOKEN = '6267872736:AAFif1GKVPKThRpBTqNqnqvX8RObPwKudN4'

WEBHOOK_HOST = 'e299-31-202-126-61.eu.ngrok.io'
WEBHOOK_PORT = 8443
WEBHOOK_LISTEN = '0.0.0.0'

WEBHOOK_URL_BASE = 'https://%s' % WEBHOOK_HOST
WEBHOOK_URL_PATH = '/%s/' % API_TOKEN

shop_bot = telebot.TeleBot(API_TOKEN)

commands = ['Add to list', 'Get list', 'Remove from list']
keyboard = telebot.types.ReplyKeyboardMarkup()
keyboard.row(*commands)

# {<chat_id>: [shopping_list, current_operation, last_message_id]}
user_data = {}


@app.route('/', methods=['GET', 'HEAD'])
def index():
    print('index')
    return 'hi!'


@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        shop_bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)


@shop_bot.message_handler(commands=['start'])
def start(message):
    shop_bot.reply_to(message, 'Welcome to shopping bot', reply_markup=keyboard)


@shop_bot.message_handler(content_types=['text'])
def command(message):
    if message.chat.id not in user_data:
        user_data[message.chat.id] = [[], None, None]
    if message.text == 'Add to list':
        user_data[message.chat.id][1] = 'add'
        shop_bot.reply_to(message, 'Add items to the list')
    elif message.text == 'Get list':
        user_data[message.chat.id][1] = 'get'
        shop_bot.reply_to(message, ', '.join(user_data[message.chat.id][0]) if user_data[message.chat.id][0] else 'Your list is empty')
    elif message.text == 'Remove from list':
        user_data[message.chat.id][1] = 'rm'
        inline_kb = telebot.types.InlineKeyboardMarkup()
        inline_kb.row_width = 2
        for elem in user_data[message.chat.id][0]:
            inline_kb.add(telebot.types.InlineKeyboardButton(elem, callback_data=elem))
        res = shop_bot.reply_to(message, 'Now you can delete item', reply_markup=inline_kb)
        user_data[message.chat.id][2] = res.message_id
    else:
        if user_data[message.chat.id][1] == 'add':
            user_data[message.chat.id][0].append(message.text)
            shop_bot.reply_to(message, f'successfully add {message.text}')


@shop_bot.callback_query_handler(func=lambda x: True)
def callback_handler(call):
    if call.data in user_data[call.message.chat.id][0]:
        user_data[call.message.chat.id][0].remove(call.data)

    inline_kb = telebot.types.InlineKeyboardMarkup()
    inline_kb.row_width = 2

    for elem in user_data[call.message.chat.id][0]:
        inline_kb.add(telebot.types.InlineKeyboardButton(elem, callback_data=elem))
    shop_bot.edit_message_reply_markup(call.message.chat.id, user_data[call.message.chat.id][2], reply_markup=inline_kb)


# shop_bot.polling()
shop_bot.remove_webhook()
time.sleep(0.1)

# Set webhook
shop_bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)

app.run(host='localhost', port=8443)
