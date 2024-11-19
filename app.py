import telebot
import requests
import json
from config import keys, TOKEN

bot = telebot.TeleBot(TOKEN)

class APIException(Exception):
    pass

class MoneyConverter:
    @staticmethod
    def get_price(base: str, quote: str, amount: str):
        if quote == base:
            raise APIException(f'Введите различные валюты: {base}.')

        try:
            base_ticker = keys[base]
        except KeyError:
            raise APIException(f'Не удалось обработать валюту {base}')
        try:
            quote_ticker = keys[quote]
        except KeyError:
            raise APIException(f'Не удалось обработать валюту {quote}')
        try:
            amount = float(amount)
        except ValueError:
            raise APIException(f'Не удалось обработать количество {amount}')

        r = requests.get(f"https://min-api.cryptocompare.com/data/price?fsym={quote_ticker}&tsyms={base_ticker}")
        total_base = json.loads(r.content)[keys[base]]


@bot.message_handler(commands=['start', 'help'])
def help(message: telebot.types.Message):
    text = 'Для начала работы введите команду в следующем формате (через пробел):' \
           ' \n- <Название валюты, цену которой Вы хотите узнать>  \n- <Название валюты, в которой Вы хотите узнать ' \
           'цену первой валюты> \n- <Количество первой валюты>\n \
 Список доступных валют: /values'

    bot.reply_to(message, text)


@bot.message_handler(commands=['values'])
def values(message: telebot.types.Message):
    text = 'Доступные валюты:'
    for key in keys.keys():
        text = '\n'.join((text, key,))
    bot.reply_to(message, text)


@bot.message_handler(content_types=['text', ])
def get_price(message: telebot.types.Message):
    try:
        values = message.text.split(' ')

        if len(values) > 3:
            raise APIException('Неверно введены параметры')
        elif len(values) != 3:
            raise APIException('Неверно введены параметры')
        elif len(values) < 3:
            raise APIException('Неверно введены параметры')


        base, quote, amount = values
        total_base = MoneyConverter.get_price(base, quote, amount)
    except APIException as e:
        bot.reply_to(f'Ошибка пользователя, \n{e}')

    except Exception as e:
        bot.reply_to(message, f'Произошла ошибка\n{e}')
    else:
        text = f'Цена {amount} {quote} в {base}: {total_base}'
        bot.send_message(message.chat.id, text)

bot.polling(none_stop=True)