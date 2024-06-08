import telebot
from groq import Groq
from config import GROQ, TOKEN
import time
from requests.exceptions import ReadTimeout
from concurrent.futures import ThreadPoolExecutor

client = Groq(api_key=GROQ)
bot = telebot.TeleBot(TOKEN)
messages = []

executor = ThreadPoolExecutor(max_workers=5)

def handle_message(message):
    global messages
    messages.append({"role": 'user', "content": message.text})
    if len(messages) > 6:
        messages = messages[-6:]

    try:
        response = client.chat.completions.create(model='llama3-70b-8192', messages=messages, temperature=0)
        response_text = response.choices[0].message.content
        bot.send_message(message.from_user.id, response_text)
        messages.append({"role": 'assistant', "content": response_text})
    except Exception as e:
        bot.send_message(message.from_user.id, f"Произошла ошибка: {e}")

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    executor.submit(handle_message, message)

def start_polling():
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=60)
        except ReadTimeout:
            print("ReadTimeout occurred, retrying in 15 seconds...")
            time.sleep(15)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            time.sleep(15)

if __name__ == "__main__":
    start_polling()
