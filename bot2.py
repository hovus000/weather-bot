import telebot
from pyowm import OWM
from apscheduler.schedulers.background import BackgroundScheduler
from pyowm.utils.config import get_default_config

config_dict = get_default_config()
config_dict['language'] = 'ru'  

owm = OWM('U_Token', config_dict)
mgr = owm.weather_manager()

bot = telebot.TeleBot('U_Token')
chat_id = 762821020

weather_translations = {
    "Clouds": "облачно ☁️",
    "Clear": "ясно ☀️",
    "Rain": "дождь 🌧️",
    "Drizzle": "морось 🌦️",
    "Thunderstorm": "гроза ⛈️",
    "Snow": "снег ❄️",
    "Mist": "туман 🌫️",
    "Fog": "туман 🌫️"
}

def load_cities():
    try:
        with open("cities.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines()]
    except:
        return ["Харьков", "Киев"] 

monitor_cities = load_cities()

def save_cities():
    with open("cities.txt", "w", encoding="utf-8") as f:
        for city in monitor_cities:
            f.write(city + "\n")

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f"Привет! Напиши название города, и я скажу какая там погода.\n\nКоманды:\n\n/add Название\n/delete Название\n/list")

@bot.message_handler(commands=['list'])
def show_cities(message):
    if not monitor_cities:
        bot.send_message(message.chat.id, "Список городов пуст.")
    else:
        text = "Твои избранные города:\n\n" + "\n".join(monitor_cities)
        bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['add'])
def add_city(message):
    try:
        city = message.text.split(maxsplit=1)[1]
        if city not in monitor_cities:
            monitor_cities.append(city)
            save_cities() 
            bot.send_message(message.chat.id, f"Город {city} добавлен!")
        else:
            bot.send_message(message.chat.id, "Этот город уже есть в списке.")
    except:
        bot.send_message(message.chat.id, "Используй: /add Название")

@bot.message_handler(commands=['delete'])
def delete_city(message):
    try:
        city = message.text.split(maxsplit=1)[1]
        if city in monitor_cities:
            monitor_cities.remove(city)
            save_cities() 
            bot.send_message(message.chat.id, f"Город {city} удален.")
        else:
            bot.send_message(message.chat.id, "Такого города нет.")
    except:
        bot.send_message(message.chat.id, "Используй: /delete Название")

@bot.message_handler(content_types=['text'])
def send_weather(message):
    try:
        city = message.text
        observation = mgr.weather_at_place(city)
        w = observation.weather
        temp = w.temperature('celsius')['temp']
        status = w.status 
        
        wether_desc = weather_translations.get(status, status)
        
        bot.send_message(message.chat.id, f"В городе {city} сейчас {wether_desc}, температура {round(temp)}°C.")
    except:
        bot.send_message(message.chat.id, "Не могу найти такой город. Попробуй написать название на английском или проверь правильность.")

def cheak_wether_monitoring():
    for city in monitor_cities:
        try:
            observation = mgr.weather_at_place(city)
            w = observation.weather
            temp = w.temperature('celsius')['temp']
            status = w.status
            
            wether_desc = weather_translations.get(status, status)
            bot.send_message(chat_id, f"🕒 Мониторинг: \n\nВ городе {city} сейчас {wether_desc}, температура {round(temp)}°C")
        except:
            continue

scheduler = BackgroundScheduler()
scheduler.add_job(cheak_wether_monitoring, 'cron', hour='*', minute=0)
scheduler.start()

print("Бот с погодой работает")
bot.infinity_polling()