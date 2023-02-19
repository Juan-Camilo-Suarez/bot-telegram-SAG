import telebot
import requests

bot = telebot.TeleBot('6019664836:AAECDCjHOmW4TpZccuXJtpwHQ3rlHBYL5_4')

print('Bot is running...')


@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")


def get_information(name: str, lastname: str, email: str, phone: str, birth_date: str) -> dict:
    url = "https://b24-iu5stq.bitrix24.site/backend_test/"
    params = {
        "CONTACT_NAME": name,
        "CONTACT_LAST_NAME": lastname,
        "CONTACT_EMAIL": email,
        "CONTACT_PHONE": phone,
        "CONTACT_BIRTHDATE": birth_date,
    }

    response = requests.post(url, params)

    return response


def fetch_information(message, name, lastname, email, phone):
    birth_date = message.text
    user = get_information(name, lastname, email, phone, birth_date)
    print(user)
    # data = user["data"]
    user_message = f'*informacion:* \n*name:* {name}\n*last name:* {lastname}\n*email:* {email}\n*telephone:* {phone}\n*birth date:* {birth_date}'
    bot.send_message(message.chat.id, "Here's your information!")
    bot.send_message(message.chat.id, user_message, parse_mode="Markdown")


def birth_date_handler(message, name, lastname, email):
    phone = message.text
    text = "What is your birth date (write it like this DD.MM.YYYY)?"
    sent_msg = bot.send_message(
        message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(
        sent_msg, fetch_information, name, lastname, email, phone)


def phone_handler(message, name, lastname):
    email = message.text
    text = "What is your telephone number?"
    sent_msg = bot.send_message(
        message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(
        sent_msg, birth_date_handler, name, lastname, email)


def email_handler(message, name):
    lastname = message.text
    text = "What is your email?"
    sent_msg = bot.send_message(
        message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(
        sent_msg, phone_handler, name, lastname)


def lastname_handler(message):
    name = message.text
    text = "What is your last name?"
    sent_msg = bot.send_message(
        message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(
        sent_msg, email_handler, name)


@bot.message_handler(commands=['form'])
def name_handler(message):
    text = "What is your name?"
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, lastname_handler)


bot.infinity_polling()
