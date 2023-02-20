from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor


CHANNEL_ID = '-channel_id'
CHANNEL_ID2 = '-channel_id2'
TOKEN = 'your_token'
PROXY_URL = "http://proxy.server:3128"
bot = Bot(token=TOKEN, parse_mode="HTML", proxy=PROXY_URL)
# Диспетчер
dp = Dispatcher(bot)

@dp.channel_post_handler(content_types=types.ContentType.ANY)
async def hand(message: types.Message):
    file = open('text.txt', 'r')
    a = file.readlines()
    for i in a:
        if i != '\n':
            i = i.replace('\n', '')
            if i in message.text:
                await bot.send_message(chat_id=CHANNEL_ID2, text=message.text)
    file.close()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
