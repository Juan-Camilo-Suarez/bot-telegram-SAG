import threading
import time
import redis
import telebot
import requests
import datetime
import pickle

bot = telebot.TeleBot('6019664836:AAECDCjHOmW4TpZccuXJtpwHQ3rlHBYL5_4')

print('Bot is running...')

url = "https://b24-iu5stq.bitrix24.site/backend_test/"

"""
service to check availability of our site
"""


def check_website(url):
    while True:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print("Website is up!")
        except:
            print("Website is down!")

        time.sleep(600)


"""
thread to check availability of our site while run bot
"""
website_thread = threading.Thread(target=check_website, args=(url,))
website_thread.start()

"""
start command
"""


@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "how are you? if you want to create form write /form")


"""
function to save information and send request in to a site
"""


def get_information(name: str, lastname: str, email: str, phone: str, birth_date: str, user_id) -> dict:
    # Read from standalone REDIS
    rd = redis.Redis(host='redis',
                     port=6379,
                     db=0,
                     )

    url = "https://b24-iu5stq.bitrix24.site/backend_test/"
    params = {
        "CONTACT_NAME": name,
        "CONTACT_LAST_NAME": lastname,
        "CONTACT_EMAIL": email,
        "CONTACT_PHONE": phone,
        "CONTACT_BIRTHDATE": birth_date,
    }
    # write a key
    user = "user-" + str(user_id)
    pickled_user = pickle.dumps(params)
    rd.set(user, pickled_user)

    response = requests.post(url, params)

    return response


"""
send information in chat before of the successful
"""


def fetch_information(message, name, lastname, email, phone):
    birth_date = message.text
    user_id = message.from_user.id
    user = get_information(name, lastname, email, phone, birth_date, user_id)
    print(user.status_code)
    user_message = f'*informacion:* \n*name:* {name}\n*last name:* {lastname}\n*email:* {email}\n*telephone:* {phone}\n*birth date:* {birth_date}'
    bot.send_message(message.chat.id, "Here's your information!")
    bot.send_message(message.chat.id, user_message, parse_mode="Markdown")
    bot.send_photo(message.chat.id, photo=open('media/successful.png', 'rb'))


"""
handler for birth date
"""


def birth_date_handler(message, name, lastname, email):
    phone = message.text
    text = "What is your birth date (write it like this DD.MM.YYYY)?"
    sent_msg = bot.send_message(
        message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(
        sent_msg, fetch_information, name, lastname, email, phone)


"""
handler for telephone number
"""


def phone_handler(message, name, lastname):
    email = message.text
    text = "What is your telephone number?"
    sent_msg = bot.send_message(
        message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(
        sent_msg, birth_date_handler, name, lastname, email)


"""
handler for email
"""


def email_handler(message, name):
    lastname = message.text
    text = "What is your email?"
    sent_msg = bot.send_message(
        message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(
        sent_msg, phone_handler, name, lastname)


"""
handler for last name
"""


def lastname_handler(message):
    name = message.text
    text = "What is your last name?"
    sent_msg = bot.send_message(
        message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(
        sent_msg, email_handler, name)


"""
handler for name
"""


@bot.message_handler(commands=['form'])
def name_handler(message):
    text = "What is your name?"
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, lastname_handler)


"""
save images from chat with users
"""


@bot.message_handler(content_types=['photo', 'audio'])
def handle_docs_photo(message):
    raw = message.photo[0].file_id
    now = datetime.datetime.now()
    date_time = now.strftime("%Y%m-%d-%H:%M")
    path = str(date_time) + str(message.from_user.id) + ".jpg"
    file_info = bot.get_file(raw)
    downloaded_file = bot.download_file(file_info.file_path)
    with open("media/" + path, 'wb') as new_file:
        new_file.write(downloaded_file)
        bot.reply_to(message, "Images Was Saved Sir")


bot.infinity_polling()
