import requests
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os
import logging

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)

API_TOKEN = '7707913796:AAFld4pmwDOndB9lcSUwe3pFFog3UKekOfQ'  # Вставьте свой токен бота

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Функция для получения chat_id
async def get_chat_id(message: types.Message):
    await message.answer(f"Ваш chat_id: {message.chat.id}")

# Регистрация обработчика для команды /chat_id
dp.message.register(get_chat_id, Command("chat_id"))

# Кнопки для запроса курса криптовалют
button_btc = KeyboardButton(text="Курс BTC")
button_eth = KeyboardButton(text="Курс ETH")
keyboards = ReplyKeyboardMarkup(keyboard=[[button_btc, button_eth]], resize_keyboard=True)

# Функция для запроса курса криптовалюты с Bybit
def get_bybit_price(symbol):
    url = f"https://api.bybit.com/v2/public/tickers?symbol={symbol}"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return f"Ошибка при запросе к Bybit: код ответа {response.status_code}"

        data = response.json()
        if "result" in data and len(data["result"]) > 0:
            price = data["result"][0]["last_price"]
            return f"Bybit: Курс {symbol} = {price} USDT"
        else:
            return "Не удалось получить данные от Bybit"
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка запроса к Bybit: {e}")
        return "Ошибка при подключении к Bybit"
    except ValueError:
        logging.error(f"Ошибка при парсинге JSON от Bybit: {response.text}")
        return "Некорректный ответ от Bybit"

# Функция для запроса курса криптовалюты с Binance
def get_binance_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return f"Ошибка при запросе к Binance: код ответа {response.status_code}"

        data = response.json()
        if "price" in data:
            price = data["price"]
            return f"Binance: Курс {symbol} = {price} USDT"
        else:
            return "Не удалось получить данные от Binance"
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка запроса к Binance: {e}")
        return "Ошибка при подключении к Binance"
    except ValueError:
        logging.error(f"Ошибка при парсинге JSON от Binance: {response.text}")
        return "Некорректный ответ от Binance"

# Обработчик команды /start
async def send_welcome(message: types.Message):
    await message.answer("Привет! Я бот для отслеживания курса криптовалют. Нажмите на кнопку для получения курса.", reply_markup=keyboards)

# Обработчик кнопок для запроса курса криптовалют
async def send_price(message: types.Message):
    symbol = "BTC" if message.text == "Курс BTC" else "ETH"

    bybit_price = get_bybit_price(symbol + "USDT")
    binance_price = get_binance_price(symbol)

    await message.answer(f"{bybit_price}\n{binance_price}")

# Функция для периодического запроса курсов
async def scheduled_price_check():
    chat_id = 192776276  # Замените на ваш chat_id или настройте получение ID
    logging.info("Запуск автоматической рассылки курсов")

    btc_price_bybit = get_bybit_price("BTCUSDT")
    eth_price_bybit = get_bybit_price("ETHUSDT")
    btc_price_binance = get_binance_price("BTC")
    eth_price_binance = get_binance_price("ETH")

    message = f"Автоматический отчет:\n\n{btc_price_bybit}\n{eth_price_bybit}\n\n{btc_price_binance}\n{eth_price_binance}"
    logging.info("Отправка автоматического сообщения")
    await bot.send_message(chat_id, message)

# Регистрация обработчиков
dp.message.register(send_welcome, Command('start'))
dp.message.register(send_price, lambda message: message.text in ["Курс BTC", "Курс ETH"])

# Настройка планировщика задач
scheduler = AsyncIOScheduler()
logging.info("Запуск планировщика задач")
scheduler.add_job(scheduled_price_check, "interval", minutes=1)  # Для тестирования, запрос раз в минуту
scheduler.start()

async def main():
    # Запуск бота (без повторного запуска планировщика)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
