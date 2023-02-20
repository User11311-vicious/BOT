import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import MediaGroup, InputFile
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.utils import executor
import aiogram.utils.markdown as md
import sqlite3
from aiogram.utils.callback_data import CallbackData
import asyncio
import random
from datetime import datetime, timedelta

conn = sqlite3.connect('database.db')
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INT,
    project_name TEXT)""")
conn.commit()


conn2 = sqlite3.connect('database2.db')
cur2 = conn2.cursor()

cur2.execute("""CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INT,
    message_id INT)""")
conn2.commit()

storage = MemoryStorage()
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
TOKEN = 'your_token'
PROXY_URL = "http://proxy.server:3128"
bot = Bot(token=TOKEN, parse_mode="HTML", proxy=PROXY_URL)
# Диспетчер
dp = Dispatcher(bot, storage=storage)
# Preview phrases
text_introduction = '<b>STEP_3D_bot</b> - Ваш интерфейс в мир 3D-технологий\n\nВыберете услугу ⤵️'
text_scan = '<b>3D-сканирование</b>\n\n•   <b>Малогабаритных объектов</b> (стационарное)\n\n•  <b>Крупногабаритных объектов</b> (ручное) \n\n•   <b>Зданий и помещений</b> (архитектурное)'
text_print = '<b>3D печать</b>\n\n•   <b>FDM</b> (простыми и инженерными пластиками)\n\n•   <b>SLA, DLP</b> (фотополимерной смолой)'
text_model = '<b>3D-моделирование</b>\n\n•  <b>Художественное</b> (полигональное)\n\n•  <b>Промышленное</b> (инженерный дизайн CAD)'
text_reverse = '<b>Реверсивный инжиниринг</b>\n\n•   <b>по физической модели</b>\n\n•   <b>по облаку точек</b> (результатам сканирования)\n\n•   <b>параметрическое моделирование</b> (твердотельное)'
text_count = '1. <b>Опишите задачу</b> удобным Вам способом (текстом, голосовым сообщением)\n\n2. <b>Прикрепите все необходимые файлы</b>, которые у Вас есть по этой задача (модели, фотографии, документы)\n\n3. Нажмите кнопку <b>Отправить задание на просчёт</b>'
worker_answer_price = 'Сколько будут стоить услуга?'
worker_answer_date = 'Сколько дней нужно на реализацию?'
worker_answer_start = 'Когда вы готовы начать?\n\nНапишите дату в формате <b>dd.mm.yy</b>\n\nПример: <b>01.01.23</b>'
text_clarification = "Вам пришло уточнение от исполнителя по заказу "
text_answer = "\n\nНажмите /answer, чтобы ответить исполнителю"
text_suggest = "Как только заказ будет готов,\nВам прийдёт сообщение с фото выполненного проекта и номером карты для оплаты.\nПосле оплаты вам пришлют готовый заказ"
ilya = 2097865080
maksim = 957486165
kirill = 332505987
daria = 1166573559
genshin = 667638178
number_of_card = '0000 0000 0000 0000'
sent_message = list()

def price_transformation(n):
    if n==1 or (n>20 and (n%10)==1) and (n%100)!=11:
        return str(n) + ' рубль'
    elif (n>1 and n<5) or (n>20 and (n%10)>1 and (n%10)<5):
        return str(n) + ' рубля'
    elif n==0 or (n> 1 and n<20) or (n%10)==0 or (n%100)>=11 or (n%10)>=5 or (n%100)>=10:
        return str(n) + ' рублей'

def date_transformation(n):
    if n==1 or (n>20 and (n%10)==1) and (n%100)!=11:
        return str(n) + ' день'
    elif (n>1 and n<5) or (n>20 and (n%10)>1 and (n%10)<5):
        return str(n) + ' дня'
    elif n==0 or (n> 1 and n<20) or (n%10)==0 or (n%100)>=11 or (n%10)>=5 or (n%100)>=10:
        return str(n) + ' дней'


class Scan(StatesGroup):
    sent_message = State()
    description = State()
    id = State()
    clarification = State()
    price = State()
    date = State()
    start = State()
    final_price = State()
    answer = State()
    end = State()
    screenshot = State()
    check = State()
    number = State()

class Reverse(StatesGroup):
    description = State()
    id = State()
    clarification = State()
    price = State()
    date = State()
    start = State()
    final_price = State()
    answer = State()
    end = State()
    screenshot = State()
    check = State()
    number = State()


class Print(StatesGroup):
    description = State()
    id = State()
    clarification = State()
    price = State()
    date = State()
    start = State()
    final_price = State()
    answer = State()
    end = State()
    screenshot = State()
    check = State()
    number = State()


class Model(StatesGroup):
    description = State()
    id = State()
    clarification = State()
    price = State()
    date = State()
    start = State()
    final_price = State()
    answer = State()
    end = State()
    screenshot = State()
    check = State()
    number = State()


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

    def add_user(self, user_id, project_name):
        with self.connection:
            return self.cursor.execute("INSERT INTO `users` (`user_id`, `project_name`) VALUES (?,?);", (user_id, project_name))

    def add_project_name(self, project_name):
        with self.connection:
            return self.cursor.execute("INSERT INTO `users` (`project_name`) VALUES (?);", (project_name,))

    def project_name_exists(self, project_name):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM `users` WHERE `project_name` = ?", (project_name,)).fetchmany(1)
            return bool(len(result))

    def print_project_names(self):
        with self.connection:
            return self.cursor.execute("SELECT `project_name` FROM `users`").fetchall()


class Basedata:
    def __init__(self, bd_file):
        self.connection = sqlite3.connect(bd_file)
        self.cursor = self.connection.cursor()
    
    def add_messages(self, user_id, message_id):
        with self.connection:
            return self.cursor.execute("INSERT INTO `users` (`user_id`, `message_id`) VALUES (?,?);", (user_id, message_id))
    
    def sent_messages(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT message_id FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()
    
    def messages_exist(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT message_id FROM `users` WHERE `user_id` = ?", (user_id,)).fetchmany(1)
            return bool(len(result))
    
    def delete_messages(self, user_id):
        with self.connection:
            return self.cursor.execute("DELETE FROM `users` WHERE `user_id` = ?", (user_id,))


db = Database('database.db')
bd = Basedata('database2.db')
id_sender = CallbackData('sender', 'action', 'id_user', 'project_name', 'price', 'time', 'begin')


# Хендлер под команду /start
@dp.message_handler(commands="start")
async def start_message(message: types.Message):
    if message.chat.type == 'private':
        db.add_user(message.from_user.id, None)
    await bot.send_message(chat_id=message.from_user.id, text=text_introduction, reply_markup=keyboard_1())


# <...3D SCAN...>
# Клавиатура под таблицу_1
def keyboard_1():
    buttons = [
        types.InlineKeyboardButton(text="3D-сканирование", callback_data='scan'),
        types.InlineKeyboardButton(text="Реверсинжиниринг", callback_data='reverse'),
        types.InlineKeyboardButton(text="3D-печать", callback_data="print"),
        types.InlineKeyboardButton(text="3D-моделирование", callback_data="model")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


#клавиатура под таблицу_2
def keyboard_scan():
    buttons = [
        types.InlineKeyboardButton(text="Оценить стоимость", callback_data="file"),
        types.InlineKeyboardButton(text="Примеры проектов", callback_data="examples_scan"),
        types.InlineKeyboardButton(text="Назад", callback_data="back")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


def keyboard_after():
    buttons = [
        types.InlineKeyboardButton(text="Назад", callback_data="back"),
        types.InlineKeyboardButton(text="Оценить стоимость", callback_data="file")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


# Клавиатура стоимости
def keyboard_file():
    buttons = [
        types.KeyboardButton(text="Назад"),
        types.KeyboardButton(text="Отправить задание на просчёт")
    ]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    keyboard.add(*buttons)
    return keyboard


# Keyboard for second example
def keyboard_more_examples_scan():
    buttons = [
        types.InlineKeyboardButton(text='Назад', callback_data='back_cost'),
        types.InlineKeyboardButton(text="Ещё", callback_data="more")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(*buttons)
    return keyboard


# Keyboard for third example
def keyboard_more3_examples_scan():
    buttons = [
        types.InlineKeyboardButton('Назад', callback_data='back_cost'),
        types.InlineKeyboardButton(text="Ещё", callback_data="more3")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(*buttons)
    return keyboard


# Клавиатура заказа
def keyboard_order(id_user, project_name, price, time, begin):
    buttons = [
        types.InlineKeyboardButton(text="Нет", callback_data=id_sender.new(action="no", id_user=id_user, project_name=project_name, price=price, time=time, begin=begin)),
        types.InlineKeyboardButton(text="Да", callback_data=id_sender.new(action="yes", id_user=id_user, project_name=project_name, price=price, time=time, begin=begin))
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


# Клавиатура подтверждения или отмены
def keyboard_order_data(id_user, project_name, price, time, begin):
    buttons = [
        types.InlineKeyboardButton(text="Нет", callback_data=id_sender.new(action="cancel", id_user=id_user, project_name=project_name, price=price, time=time, begin=begin)),
        types.InlineKeyboardButton(text="Да", callback_data=id_sender.new(action="suggest", id_user=id_user, project_name=project_name, price=price, time=time, begin=begin))
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


# Клавиатура стоимости
def keyboard_reason():
    buttons = [
        types.InlineKeyboardButton(text="Назад", callback_data="reason")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard

def keyboard_payment():
    buttons = [
        types.InlineKeyboardButton(text="Оплатить", callback_data="payment")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


def keyboard_change_price(id_user, project_name, price, time, begin):
    buttons = [
        types.InlineKeyboardButton(text="Изменить цену", callback_data=id_sender.new(action="change_price", id_user=id_user, project_name=project_name, price=price, time=time, begin=begin))
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1, one_time_keyboard=True)
    keyboard.add(*buttons)
    return keyboard

def keyboard_approve_price():
    buttons = [
        types.InlineKeyboardButton(text="Нет", callback_data="disapprove_price"),
        types.InlineKeyboardButton(text="Да", callback_data="approve_price")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


# Хендлер под команду scan
@dp.callback_query_handler(text="scan")
async def scan(call: types.CallbackQuery):
    # try:
        await bot.send_message(chat_id=call.from_user.id, text=text_scan, reply_markup=keyboard_scan())
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    # except BaseException as err:
    #     pass

@dp.callback_query_handler(text="file")
async def cost(call: types.CallbackQuery):
    # try:
        id_user_answer = call.from_user.id
        await bot.send_message(chat_id=call.from_user.id, text=text_count, reply_markup=keyboard_file())
        await Scan.description.set()
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

        @dp.message_handler(content_types=types.ContentTypes.ANY, state=Scan.description)
        async def description(message: types.Message, state: FSMContext):
            now = datetime.now()
            number = random.randint(1,1000)
            if message.text == "Отправить задание на просчёт":
                if bd.messages_exist(message.from_user.id):
                    while 1:
                        project_name = 'S.{}.{}.{}'.format(now.day, now.month, number)
                        if not db.project_name_exists(project_name):
                            db.add_project_name(str(project_name))
                            break
                        else:
                            continue
                    #ilya
                    await bot.send_message(chat_id=genshin, text="<b>НОВЫЙ ЗАКАЗ</b> '{}'\n<b>Направление:</b> 3D-Сканирование".format(project_name))
                    for i in bd.sent_messages(message.from_user.id):
                        for j in i:
                        #ilya
                            await bot.copy_message(chat_id=genshin, from_chat_id=message.from_user.id, message_id=j)
                    #ilya
                    await bot.send_message(chat_id=genshin, text="Есть вопросы по заказу?", reply_markup=keyboard_order(id_user_answer, project_name, 1, 1, 1))
                    await bot.send_message(chat_id=message.from_user.id, text="<b>Принято! Анализируем стоимость и сроки. Скоро ответим.</b>", reply_markup=types.ReplyKeyboardRemove())
                    await asyncio.sleep(5)
                    await bot.send_message(chat_id=message.from_user.id, text=text_introduction, reply_markup=keyboard_1())
                    user = message.from_user.get_current()
                    #genshin
                    await bot.send_message(chat_id=genshin, text=f'\t<b>НОВАЯ ЗАЯВКА</b>\n\n<b>Номер заказа:</b> {project_name}\n\n<b>Имя Заказчика:</b> {user["first_name"]}\n\n<b>Фамилия Заказчика:</b> {user["last_name"]}\n\n<b>Никнейм Заказчика:</b> @{user["username"]}')
                    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
                    await state.finish()
                    bd.delete_messages(message.from_user.id)
                else:
                    await bot.send_message(chat_id=message.from_user.id, text='Пришлите описание проекта, исполнителю нужно чётко понимать задачу =)')


            if message.text == "Назад":
                current_state = await state.get_state()
                if current_state is None:
                    return
                await state.finish()
                await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
                await bot.send_message(chat_id=message.from_user.id, text='Назад', reply_markup=types.ReplyKeyboardRemove())
                await bot.send_message(chat_id=message.from_user.id, text=text_scan, reply_markup=keyboard_scan())
                bd.delete_messages(message.from_user.id)
            else:
                async with state.proxy() as data:
                    if message.text != "Отправить задание на просчёт" and message.text != 'Пришлите описание проекта, исполнителю нужно чётко понимать задачу =)':
                        data['description'] = message.message_id
                        bd.add_messages(message.from_user.id, data["description"])
            # except BaseException as err:
            #     pass


# Хендлер под команде yes
@dp.callback_query_handler(id_sender.filter(action="yes"))
async def worker_yes(call: types.CallbackQuery, callback_data: dict):
    # try:
        await bot.send_message(chat_id=call.from_user.id, text="Опишите свой вопрос")
        await Scan.clarification.set()
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

        @dp.message_handler(state=Scan.clarification)
        async def clarification(message: types.Message, state: FSMContext):
            async with state.proxy() as data:
                data['clarification'] = message.text
            await bot.send_message(chat_id=callback_data["id_user"], text="{} '{}'".format(text_clarification, callback_data["project_name"]) + "\n<b>Направление: </b> 3D-Сканирование" + '\n<b>Уточнение: </b>' + data["clarification"] + '\nДля ответа нажмите /answer')
            await state.finish()
            await message.reply("Вопрос отправился заказчику, ожидайте ответа")


        @dp.message_handler(commands="answer")
        async def preset_answer(message: types.Message):
            await bot.send_message(chat_id=message.from_user.id, text="Напишите ответ на вопрос исполнителя")
            await Scan.answer.set()


        @dp.message_handler(state=Scan.answer)
        async def answer(message: types.Message, state: FSMContext):
            async with state.proxy() as data:
                data["answer"] = message.text
            #ilya
            await bot.send_message(chat_id=genshin, text="Есть вопрос по заказу '{}'".format(callback_data["project_name"]) + "?\n" + data["answer"], reply_markup=keyboard_order(message.from_user.id, callback_data["project_name"], 1, 1, 1))
            await message.reply("Ответ отправился исполнителю, ожидайте реакции")
            await state.finish()
    # except BaseException as err:
    #     pass


# Хендлер под команду no
@dp.callback_query_handler(id_sender.filter(action="no"))
async def worker_no(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    # try:
        await bot.send_message(chat_id=call.from_user.id, text=worker_answer_price)
        await Scan.id.set()
        await state.update_data(id=int(callback_data["id_user"]))
        await Scan.next()
        await state.update_data(clarification=1)
        await Scan.next()
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)


        @dp.message_handler(state=Scan.price)
        async def price(message: types.Message, state: FSMContext):
            if message.text:
                if message.text.replace(' ', '').isdigit() and message.text != "0":
                    async with state.proxy() as data:
                        data['price_Scan'] = message.text
                        data["price_Scan"] = str(data["price_Scan"]).lstrip('0').replace(' ', '')
                    await message.reply(text=worker_answer_date)
                    await Scan.next()
                else:
                    await bot.send_message(chat_id=message.from_user.id, text="Напишите цену числом (также услуга не может быть бесплатной)")
            else:
                await bot.send_message(chat_id=message.from_user.id,
                                    text="Извините, неправильный тип сообщения, пожалуйста, ответьте текстом.")

        @dp.message_handler(state=Scan.date)
        async def date(message: types.Message, state: FSMContext):
            if message.text:
                if message.text.replace(' ', '').isdigit() and message.text != "0":
                    async with state.proxy() as data:
                        data['date_Scan'] = message.text
                        data["date_Scan"] = str(data["date_Scan"]).lstrip('0')
                    await message.reply(text=worker_answer_start)
                    await Scan.next()
                else:
                    await bot.send_message(chat_id=message.from_user.id, text="Напишите количество дней числом.")
            else:
                await bot.send_message(chat_id=message.from_user.id,
                                    text="Извините, неправильный тип сообщения, пожалуйста, ответьте текстом.")


        @dp.message_handler(state=Scan.start)
        async def start(message: types.Message, state: FSMContext):
            if message.text:
                try:
                    if datetime.strptime(datetime.now().strftime("%d.%m.%y"), '%d.%m.%y').date() <= datetime.strptime(message.text, '%d.%m.%y').date():
                        async with state.proxy() as data:
                            data['start_Scan'] = message.text
                        callback_data["time"] = data["date_Scan"]
                        callback_data["begin"] = data["start_Scan"]
                        callback_data["time"] = (datetime.strptime(callback_data["begin"], '%d.%m.%y') + timedelta(days=int(data["date_Scan"]))).strftime('%d.%m.%y')
                        #gensh
                        await bot.send_message(chat_id=genshin, text="<b>Номер заказа:</b> '{}'\n<b>Направление:</b> 3D-Сканирование\n<b>Цена заказа:</b> {} \n<b>Количество дней выполнения:</b> {} \n<b>Начало выполнения:</b> {} \n<b>Конец выполнения:</b> {}".format(callback_data["project_name"], str(price_transformation(int(data["price_Scan"]))), date_transformation(int(data["date_Scan"])), data["start_Scan"], callback_data["time"]))
                        #gensh
                        await bot.send_message(chat_id=genshin, text="Укажите цену заказа '{}', нажав кнопку изменить цену\n".format(callback_data["project_name"]), reply_markup=keyboard_change_price(data["id"], callback_data["project_name"], 1, 1, 1))
                        await state.finish()
                        await bot.send_message(chat_id=message.from_user.id, text="Сообщение отправилось заказчику.")
                    else:
                        await bot.send_message(chat_id=message.from_user.id, text="Вы указали прошедшую дату, напишите реальную дату начала выполнения заказ")
                except BaseException as err:
                    # await print(err)
                    await bot.send_message(chat_id=message.from_user.id, text="Неверный формат даты, напишите через dd.mm.yy или такой даты не существует")
            else:
                await bot.send_message(chat_id=message.from_user.id,
                                    text="Извините, неправильный тип сообщения, пожалуйста, ответьте текстом.")


        @dp.callback_query_handler(id_sender.filter(action="change_price"))
        async def change_price(call: types.CallbackQuery):
            #gensh
            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
            await bot.send_message(chat_id=genshin, text="Напишите цену числом.")
            await Scan.final_price.set()

        @dp.message_handler(state=Scan.final_price)
        async def final_price(message: types.Message, state: FSMContext):
            if message.text:
                if message.text.replace(' ', '').isdigit() and message.text != "0":
                    async with state.proxy() as data:
                        data["final_price"] = message.text
                        data["final_price"] = str(data["final_price"]).lstrip('0').replace(' ', '')
                    callback_data["price"] = data["final_price"]
                    await bot.send_message(chat_id=message.from_user.id, text='Вы подтверждаете введённую цену <b>{}</b>'.format(price_transformation(int(data["final_price"]))), reply_markup=keyboard_approve_price())
                    await state.finish()
                else:
                    await bot.send_message(chat_id=message.from_user.id, text="Напишите цену числом (также услуга не может быть бесплатной)")
            else:
                await bot.send_message(chat_id=message.from_user.id, text="Извините, неправильный тип сообщения, пожалуйста, ответьте текстом.")

        @dp.callback_query_handler(text="approve_price")
        async def approve_price(call: types.CallbackQuery):
            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
            await bot.send_message(chat_id=call.from_user.id, text="Клиенту направлено КП.")
            await bot.send_message(chat_id=callback_data["id_user"], text="Мы сможем приступить к Вашему заказу <b>{}</b>. Заказ будет стоить <b>{}</b>. Закончим работы <b>{}</b>".format(callback_data["begin"], price_transformation(int(callback_data["price"])), callback_data["time"]))
            await bot.send_message(chat_id=callback_data["id_user"], text="Выполнить для Вас заказ '{}'?\n".format(callback_data["project_name"]), reply_markup=keyboard_order_data(callback_data["id_user"], callback_data["project_name"], int(callback_data["price"]), 1, 1))


        @dp.callback_query_handler(text="disapprove_price")
        async def disapprove_price(call: types.CallbackQuery):
            await change_price(call)
    # except BaseException as err:
    #     pass

@dp.callback_query_handler(id_sender.filter(action="suggest"))
async def suggest(call: types.CallbackQuery, callback_data: dict):
    # try:
        await bot.send_message(chat_id=call.from_user.id, text="Исполнитель уже работает над заказом '{}', {}".format(callback_data["project_name"], text_suggest))
        #ilya
        await bot.send_message(chat_id=genshin, text="Заказчика устроили цена и сроки, как только выполните заказ, отправьте /end")
        await bot.send_message(chat_id=call.from_user.id, text=text_introduction, reply_markup=keyboard_1())
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

        @dp.message_handler(commands="end")
        async def project_name(message: types.Message):
            await bot.send_message(chat_id=message.from_user.id, text='Введите номер проекта!')
            await Scan.end.set()

        @dp.message_handler(content_types=types.ContentTypes.ANY, state=Scan.end)
        async def catch_name(message: types.Message, state: FSMContext):
            if message.text:
                async with state.proxy() as data:
                    data["end"] = message.text

                try:
                    res = next(x[0] for x in db.print_project_names() if x[0]==data["end"])
                    await bot.send_message(chat_id=message.from_user.id, text="Прикрепите скриншот выполненной работы")
                    await Scan.next()
                except StopIteration:
                    await state.finish()
                    await bot.send_message(chat_id=message.from_user.id, text='Такого номера проекта не существует, пожалуйста, введите корректный номер проекта')
                    await project_name(message)
            else:
                await bot.send_message(chat_id=message.from_user.id, text='Пришлите числовое значение номера проекта, которое присылалось вам ранее.')

        @dp.message_handler(content_types=["photo"], state=Scan.screenshot)
        async def send_screenshot(message: types.Message, state: FSMContext):
            if message.photo:
                async with state.proxy() as data:
                    data["screenshot"] = message.photo[0].file_id
                await bot.send_message(chat_id=message.from_user.id, text="Сообщение отправилось Заказчику с предложением об оплате.")
                await bot.send_photo(chat_id=callback_data["id_user"], photo=data["screenshot"], caption="Вам пришло фото в подтверждение выполненного заказа '{}'.\n".format(callback_data["project_name"]))
                await bot.send_message(chat_id=callback_data["id_user"], text="Готовы оплатить заказ '{}' на сумму {}?\nПосле оплаты вам прийдёт готовый проект.".format(callback_data["project_name"], price_transformation(int(callback_data["price"]))), reply_markup=keyboard_payment())
                await state.finish()
            else:
                await bot.send_message(chat_id=message.from_user.id, text="Извините, неправильный тип сообщения, пожалуйста, пришлите фото.")


        @dp.callback_query_handler(text="payment")
        async def payment(call: types.CallbackQuery):
            await bot.send_message(chat_id=call.from_user.id, text="Переведите {} по карте '{}' на имя Ганьшина В.К. и не забудьте сделать скриншот перевода.\n Как только произведёте оплату нажмите /pay".format(price_transformation(int(callback_data["price"])), number_of_card))
            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

        @dp.message_handler(commands="pay")
        async def end_price(message: types.Message):
            await bot.send_message(chat_id=message.from_user.id, text='Пришлите чек об оплате')
            await Scan.check.set()

        @dp.message_handler(content_types=["photo"], state=Scan.check)
        async def check(message: types.Message, state: FSMContext):
            if message.photo:
                async with state.proxy() as data:
                    data["check"] = message.photo[0].file_id
                #genshin
                await bot.send_photo(chat_id=genshin, photo=data["check"], caption=f'Чек об оплате заказа {callback_data["project_name"]}, не забудьте связаться с заказчиком')
                await bot.send_message(chat_id=message.from_user.id, text='Ожидайте подтверждения, скоро с вами свяжутся', reply_markup=keyboard_1())
                await state.finish()
            else:
                await bot.send_message(chat_id=message.from_user.id, text="Извините, неправильный тип сообщения, пожалуйста, пришлите фото.")
    # except BaseException as err:
    #     pass


@dp.callback_query_handler(id_sender.filter(action="cancel"))
async def cancel(call: types.CallbackQuery, callback_data: dict):
    # try:
        await bot.send_message(chat_id=call.from_user.id, text="Спасибо за обратную связь!")
        await bot.send_message(chat_id=call.from_user.id, text=text_introduction, reply_markup=keyboard_1())
    # except BaseException as err:
    #     pass

# Хендлер под команду back_scan
@dp.callback_query_handler(state="*", text="back_scan1")
async def revert_scan(call: types.CallbackQuery, state: FSMContext):
    # try:
        current_state = await state.get_state()
        if current_state is None:
            return
        await state.finish()
        await bot.send_message(chat_id=call.from_user.id, text=text_scan, reply_markup=keyboard_scan())
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    # except BaseException as err:
    #     pass

# Хендлер под команду example
@dp.callback_query_handler(text="examples_scan")
async def example_1(call: types.CallbackQuery):
    # try:
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        album = MediaGroup()
        album.attach_video(video=InputFile(path_or_bytesio='/home/Akveduk/bot/3d-scan/project3/scan1.mp4'), caption='Пример №1')
        await call.message.answer_media_group(media=album)
        await call.message.answer('Больше фото проектов', reply_markup=keyboard_more_examples_scan())
    # except BaseException as err:
    #     pass

# # Handler for command example 2
@dp.callback_query_handler(text='more')
async def example_2(call: types.CallbackQuery):
    # try:
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        album = MediaGroup()
        album.attach_photo(photo=InputFile(path_or_bytesio='/home/Akveduk/bot/3d-scan/project2/scan1.jpg'), caption='Пример №2')
        album.attach_photo(photo=InputFile(path_or_bytesio='/home/Akveduk/bot/3d-scan/project2/scan2.jpg'))
        await call.message.answer_media_group(media=album)
        await call.message.answer('Больше фото проектов', reply_markup=keyboard_more3_examples_scan())
    # except BaseException as err:
    #     pass

# Handler for command example 3
@dp.callback_query_handler(text='more3')
async def example_3(call: types.CallbackQuery):
    # try:
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        album = MediaGroup()
        album.attach_photo(photo=InputFile(path_or_bytesio='/home/Akveduk/bot/3d-scan/project1/scan1.jpg'), caption='Пример №3')
        album.attach_photo(photo=InputFile(path_or_bytesio='/home/Akveduk/bot/3d-scan/project1/scan4.jpg'))
        await call.message.answer_media_group(media=album)
        await call.message.answer('Было представлено достаточно примеров для того, чтобы принять решение. Пора приступать к оценке стоимости своего проекта!', reply_markup=keyboard_after())
    # except BaseException as err:
    #     pass

# Хендлер под команду back
@dp.callback_query_handler(text="back")
async def reset_scan(call: types.CallbackQuery):
    # try:
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await bot.send_message(chat_id=call.from_user.id, text=text_introduction, reply_markup=keyboard_1())
    # except BaseException as err:
    #     pass

# Хендлер под команду back
@dp.callback_query_handler(text="back_cost")
async def back_cost(call: types.CallbackQuery):
    # try:
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await bot.send_message(chat_id=call.from_user.id, text=text_introduction, reply_markup=keyboard_scan())
    # except BaseException as err:
    #     pass




























#<...Reverse...>
#клавиатура под таблицу_2
def keyboard_reverse():
    buttons = [
        types.InlineKeyboardButton(text="Оценить стоимость", callback_data="file_reverse"),
        types.InlineKeyboardButton(text="Примеры проектов", callback_data="examples_reverse"),
        types.InlineKeyboardButton(text="Назад", callback_data="back_reverse")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


def keyboard_after_reverse():
    buttons = [
        types.InlineKeyboardButton(text="Назад", callback_data="back_reverse"),
        types.InlineKeyboardButton(text="Оценить стоимость", callback_data="file_reverse")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


# Клавиатура стоимости
def keyboard_file_reverse():
    buttons = [
        types.KeyboardButton(text="Назад"),
        types.KeyboardButton(text="Отправить задание на просчёт")
    ]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    keyboard.add(*buttons)
    return keyboard


# Keyboard for second example
def keyboard_more_examples_reverse():
    buttons = [
        types.InlineKeyboardButton(text='Назад', callback_data='back_cost_reverse'),
        types.InlineKeyboardButton(text="Ещё", callback_data="more_reverse")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(*buttons)
    return keyboard


# Keyboard for third example
def keyboard_more3_examples_reverse():
    buttons = [
        types.InlineKeyboardButton('Назад', callback_data='back_cost_reverse'),
        types.InlineKeyboardButton(text="Ещё", callback_data="more_reverse3")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(*buttons)
    return keyboard


# Клавиатура заказа
def keyboard_order_reverse(id_user, project_name, price, time, begin):
    buttons = [
        types.InlineKeyboardButton(text="Нет", callback_data=id_sender.new(action="no_reverse", id_user=id_user, project_name=project_name, price=price, time=time, begin=begin)),
        types.InlineKeyboardButton(text="Да", callback_data=id_sender.new(action="yes_reverse", id_user=id_user, project_name=project_name, price=price, time=time, begin=begin))
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


# Клавиатура подтверждения или отмены
def keyboard_order_data_reverse(id_user, project_name, price, time, begin):
    buttons = [
        types.InlineKeyboardButton(text="Нет", callback_data=id_sender.new(action="cancel_reverse", id_user=id_user, project_name=project_name, price=price, time=time, begin=begin)),
        types.InlineKeyboardButton(text="Да", callback_data=id_sender.new(action="suggest_reverse", id_user=id_user, project_name=project_name, price=price, time=time, begin=begin))
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


# Клавиатура стоимости
def keyboard_reason_reverse():
    buttons = [
        types.InlineKeyboardButton(text="Назад", callback_data="reason_reverse")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard

def keyboard_payment_reverse():
    buttons = [
        types.InlineKeyboardButton(text="Оплатить", callback_data="payment_reverse")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


def keyboard_change_price_reverse(id_user, project_name, price, time, begin):
    buttons = [
        types.InlineKeyboardButton(text="Изменить цену", callback_data=id_sender.new(action="change_price_reverse", id_user=id_user, project_name=project_name, price=price, time=time, begin=begin))
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


def keyboard_approve_price_reverse():
    buttons = [
        types.InlineKeyboardButton(text="Нет", callback_data="disapprove_price_reverse"),
        types.InlineKeyboardButton(text="Да", callback_data="approve_price_reverse")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


# Хендлер под команду scan
@dp.callback_query_handler(text="reverse")
async def reverse(call: types.CallbackQuery):
    try:
        await bot.send_message(chat_id=call.from_user.id, text=text_model, reply_markup=keyboard_reverse())
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    except BaseException as err:
        pass

@dp.callback_query_handler(text="file_reverse")
async def cost_reverse(call: types.CallbackQuery):
    try:
        id_user_answer = call.from_user.id
        await bot.send_message(chat_id=call.from_user.id, text=text_count, reply_markup=keyboard_file_reverse())
        await Reverse.description.set()
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)


        @dp.message_handler(content_types=types.ContentTypes.ANY, state=Reverse.description)
        async def description_reverse(message: types.Message, state: FSMContext):
            now = datetime.now()
            number = random.randint(1,1000)
            if message.text == "Отправить задание на просчёт":
                if bd.messages_exist(message.from_user.id):
                    while 1:
                        project_name = 'R.{}.{}.{}'.format(now.day, now.month, number)
                        if not db.project_name_exists(project_name):
                            db.add_project_name(str(project_name))
                            break
                        else:
                            continue
                    #ilya
                    await bot.send_message(chat_id=genshin, text="<b>НОВЫЙ ЗАКАЗ</b> '{}'\n<b>Направление:</b> Реверсинжиниринг".format(project_name))
                    #ilya
                    for i in bd.sent_messages(message.from_user.id):
                        for j in i:
                        #ilya
                            await bot.copy_message(chat_id=genshin, from_chat_id=message.from_user.id, message_id=j)
                    #ilya
                    await bot.send_message(chat_id=genshin, text="Есть вопросы по заказу?", reply_markup=keyboard_order_reverse(id_user_answer, project_name, 1, 1, 1))
                    await bot.send_message(chat_id=message.from_user.id, text="<b>Принято! Анализируем стоимость и сроки. Скоро ответим.</b>", reply_markup=types.ReplyKeyboardRemove())
                    await bot.send_message(chat_id=message.from_user.id, text=text_introduction, reply_markup=keyboard_1())
                    user = message.from_user.get_current()
                    #genshin
                    await bot.send_message(chat_id=genshin, text=f'\t<b>НОВАЯ ЗАЯВКА</b>\n\n<b>Номер заказа:</b> {project_name}\n\n<b>Имя Заказчика:</b> {user["first_name"]}\n\n<b>Фамилия Заказчика:</b> {user["last_name"]}\n\n<b>Никнейм Заказчика:</b> @{user["username"]}')
                    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
                    await state.finish()
                    bd.delete_messages(message.from_user.id)
                else:
                    await bot.send_message(chat_id=message.from_user.id, text='Пришлите описание проекта, исполнителю нужно чётко понимать задачу =)')

            if message.text == "Назад":
                current_state = await state.get_state()
                if current_state is None:
                    return
                await state.finish()
                await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
                await bot.send_message(chat_id=message.from_user.id, text='Назад', reply_markup=types.ReplyKeyboardRemove())
                await bot.send_message(chat_id=message.from_user.id, text=text_reverse, reply_markup=keyboard_reverse())
                bd.delete_messages(message.from_user.id)
            else:
                async with state.proxy() as data:
                    if message.text != "Отправить задание на просчёт" and message.text != 'Пришлите описание проекта, исполнителю нужно чётко понимать задачу =)':
                        data['description'] = message.message_id
                        bd.add_messages(message.from_user.id, data["description"])
    except BaseException as err:
        pass


# Хендлер под команде yes
@dp.callback_query_handler(id_sender.filter(action="yes_reverse"))
async def worker_yes_reverse(call: types.CallbackQuery, callback_data: dict):
    try:
        callback_data["id_user"] = call.from_user.id
        await bot.send_message(chat_id=call.from_user.id, text="Опишите свой вопрос")
        await Reverse.clarification.set()
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)


        @dp.message_handler(state=Reverse.clarification)
        async def clarification_reverse(message: types.Message, state: FSMContext):
            async with state.proxy() as data:
                data['clarification'] = message.text
            await bot.send_message(chat_id=callback_data["id_user"], text="{} '{}'".format(text_clarification, callback_data["project_name"]) + "\n<b>Направление: </b> Реверсинжиниринг" + '\n<b>Уточнение: </b>' + data["clarification"] + '\nДля ответа нажмите /answer')
            await state.finish()
            await message.reply("Вопрос отправился заказчику, ожидайте ответа")


        @dp.message_handler(commands="answer")
        async def preset_answer_reverse(message: types.Message):
            await bot.send_message(chat_id=message.from_user.id, text="Напишите ответ на вопрос исполнителя")
            await Reverse.answer.set()


        @dp.message_handler(state=Reverse.answer)
        async def answer_reverse(message: types.Message, state: FSMContext):
            async with state.proxy() as data:
                data["answer"] = message.text
            #ilya
            await bot.send_message(chat_id=genshin, text="Есть вопрос по заказу '{}'".format(callback_data["project_name"]) + "?\n" + data["answer"], reply_markup=keyboard_order_reverse(message.from_user.id, callback_data["project_name"], 1, 1, 1))
            await message.reply("Ответ отправился исполнителю, ожидайте реакции")
            await state.finish()
    except BaseException as err:
        pass

# Хендлер под команду no
@dp.callback_query_handler(id_sender.filter(action="no_reverse"))
async def worker_no_reverse(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    try:
        await bot.send_message(chat_id=call.from_user.id, text=worker_answer_price)
        await Reverse.id.set()
        await state.update_data(id=int(callback_data["id_user"]))
        await Reverse.next()
        await state.update_data(clarification=1)
        await Reverse.next()
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)



        @dp.message_handler(state=Reverse.price)
        async def price_reverse(message: types.Message, state: FSMContext):
            if message.text:
                if message.text.replace(' ', '').isdigit() and message.text != "0":
                    async with state.proxy() as data:
                        data['price_Reverse'] = message.text
                        data["price_Reverse"] = str(data["price_Reverse"]).lstrip('0').replace(' ', '')
                    await message.reply(text=worker_answer_date)
                    await Reverse.next()
                else:
                    await bot.send_message(chat_id=message.from_user.id, text="Напишите цену числом (также услуга не может быть бесплатной)")
            else:
                await bot.send_message(chat_id=message.from_user.id, text="Извините, неправильный тип сообщения, пожалуйста, ответьте текстом.")


        @dp.message_handler(state=Reverse.date)
        async def date_reverse(message: types.Message, state: FSMContext):
            if message.text:
                if message.text.replace(' ', '').isdigit() and message.text != "0":
                    async with state.proxy() as data:
                        data['date_Reverse'] = message.text
                        data["date_Reverse"] = str(data["date_Reverse"]).lstrip('0')
                    await message.reply(text=worker_answer_start)
                    await Reverse.next()
                else:
                    await bot.send_message(chat_id=message.from_user.id, text="Напишите количество дней числом.")
            else:
                await bot.send_message(chat_id=message.from_user.id,
                                    text="Извините, неправильный тип сообщения, пожалуйста, ответьте текстом.")


        @dp.message_handler(state=Reverse.start)
        async def start_reverse(message: types.Message, state: FSMContext):
            if message.text:
                try:
                    if datetime.strptime(datetime.now().strftime("%d.%m.%y"), '%d.%m.%y').date() <= datetime.strptime(message.text, '%d.%m.%y').date():
                        async with state.proxy() as data:
                            data['start_Reverse'] = message.text
                        callback_data["time"] = data["date_Reverse"]
                        callback_data["begin"] = data["start_Reverse"]
                        callback_data["time"] = (datetime.strptime(callback_data["begin"], '%d.%m.%y') + timedelta(days=int(data["date_Reverse"]))).strftime('%d.%m.%y')
                        #ilya
                        await bot.send_message(chat_id=genshin, text="<b>Номер заказа:</b> '{}'\n<b>Направление:</b> Реверсинжиниринг\n<b>Цена заказа:</b> {} \n<b>Количество дней выполнения:</b> {} \n<b>Начало выполнения:</b> {} \n<b>Конец выполнения:</b> {}".format(callback_data["project_name"], price_transformation(int(data["price_Reverse"])), date_transformation(int(data["date_Reverse"])), data["start_Reverse"], callback_data["time"]))
                        #ilya
                        await bot.send_message(chat_id=genshin, text="Укажите цену заказа '{}', нажав кнопку изменить цену\n".format(callback_data["project_name"]), reply_markup=keyboard_change_price_reverse(data["id"], callback_data["project_name"], 1, 1, 1))
                        await state.finish()
                        await bot.send_message(chat_id=message.from_user.id, text="Сообщение отправилось заказчику.")
                    else:
                        await bot.send_message(chat_id=message.from_user.id, text="Вы указали прошедшую дату, напишите реальную дату начала выполнения заказ")
                except BaseException as err:
                    # await print(err)
                    await bot.send_message(chat_id=message.from_user.id, text="Неверный формат даты, напишите через dd.mm.yy или такой даты не существует")
            else:
                await bot.send_message(chat_id=message.from_user.id,
                                    text="Извините, неправильный тип сообщения, пожалуйста, ответьте текстом.")


        @dp.callback_query_handler(id_sender.filter(action="change_price_reverse"))
        async def change_price_reverse(call: types.CallbackQuery):
            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
            #genshin
            await bot.send_message(chat_id=genshin, text="Напишите цену числом.")
            await Reverse.final_price.set()

        @dp.message_handler(state=Reverse.final_price)
        async def final_price_reverse(message: types.Message, state: FSMContext):
            if message.text:
                if message.text.replace(' ', '').isdigit() and message.text != "0":
                    async with state.proxy() as data:
                        data["final_price"] = message.text
                        data["final_price"] = str(data["final_price"]).lstrip('0').replace(' ', '')
                    callback_data["price"] = data["final_price"]
                    await bot.send_message(chat_id=message.from_user.id, text='Вы подтверждаете введённую цену <b>{}</b>'.format(price_transformation(int(data["final_price"]))), reply_markup=keyboard_approve_price_reverse())
                    await state.finish()
                else:
                    await bot.send_message(chat_id=message.from_user.id, text="Напишите цену числом (также услуга не может быть бесплатной)")
            else:
                await bot.send_message(chat_id=message.from_user.id, text="Извините, неправильный тип сообщения, пожалуйста, ответьте текстом.")

        @dp.callback_query_handler(text="approve_price_reverse")
        async def approve_price_reverse(call: types.CallbackQuery):
            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
            await bot.send_message(chat_id=call.from_user.id, text="Клиенту направлено КП.")
            await bot.send_message(chat_id=callback_data["id_user"], text="Мы сможем приступить к Вашему заказу <b>{}</b>. Заказ будет стоить <b>{}</b>. Закончим работы <b>{}</b>".format(callback_data["begin"], price_transformation(int(callback_data["price"])), callback_data["time"]))
            await bot.send_message(chat_id=callback_data["id_user"], text="Выполнить для Вас заказ '{}'?\n".format(callback_data["project_name"]), reply_markup=keyboard_order_data_reverse(callback_data["id_user"], callback_data["project_name"], int(callback_data["price"]), 1, 1))


        @dp.callback_query_handler(text="disapprove_price_reverse")
        async def disapprove_price_reverse(call: types.CallbackQuery):
            await change_price_reverse(call)
    except BaseException as err:
        pass



@dp.callback_query_handler(id_sender.filter(action="suggest_reverse"))
async def suggest_reverse(call: types.CallbackQuery, callback_data: dict):
    try:
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await bot.send_message(chat_id=call.from_user.id, text="Исполнитель уже работает над заказом '{}', {}".format(callback_data["project_name"], text_suggest))
        #ilya
        await bot.send_message(chat_id=genshin, text="Заказчика устроили цена и сроки, как только выполните заказ, отправьте /end")
        await bot.send_message(chat_id=call.from_user.id, text=text_introduction, reply_markup=keyboard_1())

        @dp.message_handler(commands="end")
        async def project_name_reverse(message: types.Message):
            await bot.send_message(chat_id=message.from_user.id, text='Введите номер проекта!')
            await Reverse.end.set()

        @dp.message_handler(content_types=types.ContentTypes.ANY, state=Reverse.end)
        async def catch_name_reverse(message: types.Message, state: FSMContext):
            async with state.proxy() as data:
                data["end"] = message.text
            try:
                res = next(x[0] for x in db.print_project_names() if x[0]==data["end"])
                await bot.send_message(chat_id=message.from_user.id, text="Прикрепите скриншот выполненной работы")
                await Reverse.next()
            except StopIteration:
                await state.finish()
                await bot.send_message(chat_id=message.from_user.id, text='Такого номера проекта не существует, пожалуйста, введите корректное номер проекта')
                await project_name_reverse(message)

        @dp.message_handler(content_types=["photo"], state=Reverse.screenshot)
        async def send_screenshot_reverse(message: types.Message, state: FSMContext):
            if message.photo:
                async with state.proxy() as data:
                    data["screenshot"] = message.photo[0].file_id
                await bot.send_message(chat_id=message.from_user.id, text="Сообщение отправилось Заказчику с предложением об оплате.")
                await bot.send_photo(chat_id=callback_data["id_user"], photo=data["screenshot"], caption="Вам пришло фото в подтверждение выполненного заказа '{}'.\n".format(callback_data["project_name"]))
                await bot.send_message(chat_id=callback_data["id_user"], text="Готовы оплатить заказ '{}' на сумму {}?\nПосле оплаты вам прийдёт готовый проект.".format(callback_data["project_name"], price_transformation(int(callback_data["price"]))), reply_markup=keyboard_payment_reverse())
                await state.finish()
            else:
                await bot.send_message(chat_id=message.from_user.id, text="Извините, неправильный тип сообщения, пожалуйста, пришлите фото.")

        @dp.callback_query_handler(text="payment_reverse")
        async def payment_reverse(call: types.CallbackQuery):
            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
            await bot.send_message(chat_id=call.from_user.id, text="Переведите {} по карте '{}' на имя Ганьшина В.К. и не забудьте сделать скриншот перевода.\n Как только произведёте оплату нажмите /pay".format(price_transformation(int(callback_data["price"])), number_of_card))

        @dp.message_handler(commands="pay")
        async def end_price_reverse(message: types.Message):
            await bot.send_message(chat_id=message.from_user.id, text='Пришлите чек об оплате')
            await Reverse.check.set()

        @dp.message_handler(content_types=["photo"], state=Reverse.check)
        async def check_reverse(message: types.Message, state: FSMContext):
            if message.photo:
                async with state.proxy() as data:
                    data["screenshot"] = message.message_id
                    await bot.send_message(chat_id=message.from_user.id, text='Пришлите свой номер')
                await Reverse.next()
            else:
                await bot.send_message(chat_id=message.from_user.id, text="Извините, неправильный тип сообщения, пожалуйста, пришлите фото.")
    except BaseException as err:
        pass


@dp.callback_query_handler(id_sender.filter(action="cancel_reverse"))
async def cancel_reverse(call: types.CallbackQuery, callback_data: dict):
    try:
        await bot.send_message(chat_id=call.from_user.id, text="Спасибо за обратную связь!")
        await bot.send_message(chat_id=call.from_user.id, text=text_introduction, reply_markup=keyboard_1())
    except BaseException as err:
        pass

# Хендлер под команду back_scan
@dp.callback_query_handler(state="*", text="back_reverse1")
async def revert_reverse(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        current_state = await state.get_state()
        if current_state is None:
            return
        await state.finish()
        await bot.send_message(chat_id=call.from_user.id, text=text_scan, reply_markup=keyboard_reverse())
    except BaseException as err:
        pass


# Хендлер под команду example
@dp.callback_query_handler(text="examples_reverse")
async def example_reverse1(call: types.CallbackQuery):
    try:
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        album = MediaGroup()
        album.attach_photo(photo=InputFile(path_or_bytesio='/home/Akveduk/bot/reverse/project1/rev1.jpg'), caption='Пример №1')
        album.attach_photo(photo=InputFile(path_or_bytesio='/home/Akveduk/bot/reverse/project1/rev2.jpg'))
        album.attach_photo(photo=InputFile(path_or_bytesio='/home/Akveduk/bot/reverse/project1/rev3.jpg'))
        album.attach_photo(photo=InputFile(path_or_bytesio='/home/Akveduk/bot/reverse/project1/rev4.jpg'))
        album.attach_photo(photo=InputFile(path_or_bytesio='/home/Akveduk/bot/reverse/project1/rev5.jpg'))
        await call.message.answer_media_group(media=album)
        await call.message.answer('Больше фото проектов', reply_markup=keyboard_more_examples_reverse())
    except BaseException as err:
        pass


# Хендлер под команду example
@dp.callback_query_handler(text="more_reverse")
async def example_reverse1(call: types.CallbackQuery):
    try:
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        album = MediaGroup()
        album.attach_photo(photo=InputFile(path_or_bytesio='/home/Akveduk/bot/3d-model/project3/mod1.jpg'), caption='Пример №2')
        album.attach_photo(photo=InputFile(path_or_bytesio='/home/Akveduk/bot/3d-model/project3/mod2.jpg'))
        album.attach_photo(photo=InputFile(path_or_bytesio='/home/Akveduk/bot/3d-model/project3/mod3.jpg'))
        await call.message.answer_media_group(media=album)
        await call.message.answer('Больше фото проектов', reply_markup=keyboard_more3_examples_reverse())
    except BaseException as err:
        pass


# # Handler for command example 2
@dp.callback_query_handler(text='more_reverse3')
async def example_reverse2(call: types.CallbackQuery):
    try:
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        album = MediaGroup()
        album.attach_video(video=InputFile(path_or_bytesio='/home/Akveduk/bot/reverse/project2/rev1.mp4'), caption='Пример №3')
        await call.message.answer_media_group(media=album)
        await call.message.answer('Было представлено достаточно примеров для того, чтобы принять решение. Пора приступать к оценке стоимости своего проекта!', reply_markup=keyboard_after_reverse())
    except BaseException as err:
        pass

# Хендлер под команду back
@dp.callback_query_handler(text="back_reverse")
async def reset_reverse(call: types.CallbackQuery):
    try:
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await bot.send_message(chat_id=call.from_user.id, text=text_introduction, reply_markup=keyboard_1())
    except BaseException as err:
        pass

# Хендлер под команду back
@dp.callback_query_handler(text="back_cost_reverse")
async def back_cost_reverse(call: types.CallbackQuery):
    try:
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await bot.send_message(chat_id=call.from_user.id, text=text_introduction, reply_markup=keyboard_reverse())
    except BaseException as err:
        pass






























#<...3D-Printing...>
#клавиатура под таблицу_2
def keyboard_print():
    buttons = [
        types.InlineKeyboardButton(text="Оценить стоимость", callback_data="file_print"),
        types.InlineKeyboardButton(text="Примеры проектов", callback_data="examples_print"),
        types.InlineKeyboardButton(text="Назад", callback_data="back_print")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


def keyboard_after_print():
    buttons = [
        types.InlineKeyboardButton(text="Назад", callback_data="back_print"),
        types.InlineKeyboardButton(text="Оценить стоимость", callback_data="file_print")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


# Клавиатура стоимости
def keyboard_file_print():
    buttons = [
        types.KeyboardButton(text="Назад"),
        types.KeyboardButton(text="Отправить задание на просчёт")
    ]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    keyboard.add(*buttons)
    return keyboard


# Keyboard for second example
def keyboard_more_examples_print():
    buttons = [
        types.InlineKeyboardButton(text='Назад', callback_data='back_cost_print'),
        types.InlineKeyboardButton(text="Ещё", callback_data="more_print")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(*buttons)
    return keyboard


# Клавиатура заказа
def keyboard_order_print(id_user, project_name, price, time, begin):
    buttons = [
        types.InlineKeyboardButton(text="Нет", callback_data=id_sender.new(action="no_print", id_user=id_user, project_name=project_name, price=price, time=time, begin=begin)),
        types.InlineKeyboardButton(text="Да", callback_data=id_sender.new(action="yes_print", id_user=id_user, project_name=project_name, price=price, time=time, begin=begin))
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


# Клавиатура подтверждения или отмены
def keyboard_order_data_print(id_user, project_name, price, time, begin):
    buttons = [
        types.InlineKeyboardButton(text="Нет", callback_data=id_sender.new(action="cancel_print", id_user=id_user, project_name=project_name, price=price, time=time, begin=begin)),
        types.InlineKeyboardButton(text="Да", callback_data=id_sender.new(action="suggest_print", id_user=id_user, project_name=project_name, price=price, time=time, begin=begin))
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


# Клавиатура стоимости
def keyboard_reason_print():
    buttons = [
        types.InlineKeyboardButton(text="Назад", callback_data="reason_print")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard

def keyboard_payment_print():
    buttons = [
        types.InlineKeyboardButton(text="Оплатить", callback_data="payment_print")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


def keyboard_change_price_print(id_user, project_name, price, time, begin):
    buttons = [
        types.InlineKeyboardButton(text="Изменить цену", callback_data=id_sender.new(action="change_price_print", id_user=id_user, project_name=project_name, price=price, time=time, begin=begin))
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard

def keyboard_approve_price_print():
    buttons = [
        types.InlineKeyboardButton(text="Нет", callback_data="disapprove_price_print"),
        types.InlineKeyboardButton(text="Да", callback_data="approve_price_print")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


# Хендлер под команду scan
@dp.callback_query_handler(text="print")
async def print(call: types.CallbackQuery):
    try:
        await bot.send_message(chat_id=call.from_user.id, text=text_print, reply_markup=keyboard_print())
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    except BaseException as err:
        pass


@dp.callback_query_handler(text="file_print")
async def cost_print(call: types.CallbackQuery):
    try:
        id_user_answer = call.from_user.id
        await bot.send_message(chat_id=call.from_user.id, text=text_count, reply_markup=keyboard_file_print())
        await Print.description.set()
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)


        @dp.message_handler(content_types=types.ContentTypes.ANY, state=Print.description)
        async def description_print(message: types.Message, state: FSMContext):
            now = datetime.now()
            number = random.randint(1,1000)
            if message.text == "Отправить задание на просчёт":
                if bd.messages_exist(message.from_user.id):
                    while 1:
                        project_name = 'P.{}.{}.{}'.format(now.day, now.month, number)
                        if not db.project_name_exists(project_name):
                            db.add_project_name(str(project_name))
                            break
                        else:
                            continue
                    #kirill
                    await bot.send_message(chat_id=genshin, text="<b>НОВЫЙ ЗАКАЗ</b> '{}'\n<b>Направление:</b> 3D-Печать".format(project_name))
                    for i in bd.sent_messages(message.from_user.id):
                        for j in i:
                        #kirill
                            await bot.copy_message(chat_id=genshin, from_chat_id=message.from_user.id, message_id=j)
                    #kirill
                    await bot.send_message(chat_id=genshin, text="Есть вопросы по заказу?", reply_markup=keyboard_order_print(id_user_answer, project_name, 1, 1, 1))
                    await bot.send_message(chat_id=message.from_user.id, text="<b>Принято! Анализируем стоимость и сроки. Скоро ответим.</b>", reply_markup=types.ReplyKeyboardRemove())
                    await bot.send_message(chat_id=message.from_user.id, text=text_introduction, reply_markup=keyboard_1())
                    user = message.from_user.get_current()
                    #genshin
                    await bot.send_message(chat_id=genshin, text=f'\t<b>НОВАЯ ЗАЯВКА</b>\n\n<b>Номер заказа:</b> {project_name}\n\n<b>Имя Заказчика:</b> {user["first_name"]}\n\n<b>Фамилия Заказчика:</b> {user["last_name"]}\n\n<b>Никнейм Заказчика:</b> @{user["username"]}')
                    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
                    await state.finish()
                    bd.delete_messages(message.from_user.id)
                else:
                    await bot.send_message(chat_id=message.from_user.id, text='Пришлите описание проекта, исполнителю нужно чётко понимать задачу =)')

            if message.text == "Назад":
                current_state = await state.get_state()
                if current_state is None:
                    return
                await state.finish()
                await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
                await bot.send_message(chat_id=message.from_user.id, text='Назад', reply_markup=types.ReplyKeyboardRemove())
                await bot.send_message(chat_id=message.from_user.id, text=text_print, reply_markup=keyboard_print())
                bd.delete_messages(message.from_user.id)
            else:
                async with state.proxy() as data:
                    if message.text != "Отправить задание на просчёт" and message.text != 'Пришлите описание проекта, исполнителю нужно чётко понимать задачу =)':
                        data['description'] = message.message_id
                        bd.add_messages(message.from_user.id, data["description"])
    except BaseException as err:
        pass

# Хендлер под команде yes
@dp.callback_query_handler(id_sender.filter(action="yes_print"))
async def worker_yes_print(call: types.CallbackQuery, callback_data: dict):
    try:
        callback_data["id_user"] = call.from_user.id
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await bot.send_message(chat_id=call.from_user.id, text="Опишите свой вопрос")
        await Print.clarification.set()


        @dp.message_handler(state=Print.clarification)
        async def clarification_print(message: types.Message, state: FSMContext):
            async with state.proxy() as data:
                data['clarification'] = message.text
            await bot.send_message(chat_id=callback_data["id_user"], text="{} '{}'".format(text_clarification, callback_data["project_name"]) + "\n<b>Направление: </b> 3D-печать" + '\n<b>Уточнение: </b>' + data["clarification"] + '\nДля ответа нажмите /answer')
            await state.finish()
            await message.reply("Вопрос отправился заказчику, ожидайте ответа")


        @dp.message_handler(commands="answer")
        async def preset_answer_print(message: types.Message):
            await bot.send_message(chat_id=message.from_user.id, text="Напишите ответ на вопрос исполнителя")
            await Print.answer.set()


        @dp.message_handler(state=Print.answer)
        async def answer_print(message: types.Message, state: FSMContext):
            async with state.proxy() as data:
                data["answer"] = message.text
            #kirill
            await bot.send_message(chat_id=genshin, text="Есть вопрос по заказу '{}'".format(callback_data["project_name"]) + "?\n" + data["answer"], reply_markup=keyboard_order_print(message.from_user.id, callback_data["project_name"], 1, 1, 1))
            await message.reply("Ответ отправился исполнителю, ожидайте реакции")
            await state.finish()
    except BaseException as err:
        pass

# Хендлер под команду no
@dp.callback_query_handler(id_sender.filter(action="no_print"))
async def worker_no_print(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    try:
        await bot.send_message(chat_id=call.from_user.id, text=worker_answer_price)
        await Print.id.set()
        await state.update_data(id=int(callback_data["id_user"]))
        await Print.next()
        await state.update_data(clarification=1)
        await Print.next()
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)


        @dp.message_handler(state=Print.price)
        async def price_print(message: types.Message, state: FSMContext):
            if message.text:
                if message.text.replace(' ', '').isdigit() and message.text != "0":
                    async with state.proxy() as data:
                        data['price_Print'] = message.text
                        data["price_Print"] = str(data["price_Print"]).lstrip('0').replace(' ', '')
                    await message.reply(text=worker_answer_date)
                    await Print.next()
                else:
                    await bot.send_message(chat_id=message.from_user.id, text="Напишите цену числом (также услуга не может быть бесплатной)")
            else:
                await bot.send_message(chat_id=message.from_user.id,
                                    text="Извините, неправильный тип сообщения, пожалуйста, ответьте текстом.")


        @dp.message_handler(state=Print.date)
        async def date_print(message: types.Message, state: FSMContext):
            if message.text:
                if message.text.replace(' ', '').isdigit() and message.text != "0":
                    async with state.proxy() as data:
                        data['date_Print'] = message.text
                        data["date_Print"] = str(data["date_Print"]).lstrip('0')
                    await message.reply(text=worker_answer_start)
                    await Print.next()
                else:
                    await bot.send_message(chat_id=message.from_user.id, text="Напишите количество дней числом.")
            else:
                await bot.send_message(chat_id=message.from_user.id,
                                    text="Извините, неправильный тип сообщения, пожалуйста, ответьте текстом.")


        @dp.message_handler(state=Print.start)
        async def start_print(message: types.Message, state: FSMContext):
            if message.text:
                try:
                    if datetime.strptime(datetime.now().strftime("%d.%m.%y"), '%d.%m.%y').date() <= datetime.strptime(message.text, '%d.%m.%y').date():
                        async with state.proxy() as data:
                            data['start_Print'] = message.text
                        callback_data["time"] = data["date_Print"]
                        callback_data["begin"] = data["start_Print"]
                        callback_data["time"] = (datetime.strptime(callback_data["begin"], '%d.%m.%y') + timedelta(days=int(data["date_Print"]))).strftime('%d.%m.%y')
                        #kirill
                        await bot.send_message(chat_id=genshin, text="<b>Номер заказа:</b> '{}'\n<b>Направление:</b> 3D-Печать\n<b>Цена заказа:</b> {} \n<b>Количество дней выполнения:</b> {} \n<b>Начало выполнения:</b> {} \n<b>Конец выполнения:</b> {}".format(callback_data["project_name"], price_transformation(int(data["price_Print"])), date_transformation(int(data["date_Print"])), data["start_Print"], callback_data["time"]))
                        #kirill
                        await bot.send_message(chat_id=genshin, text="Укажите цену заказа '{}', нажав кнопку изменить цену\n".format(callback_data["project_name"]), reply_markup=keyboard_change_price_print(data["id"], callback_data["project_name"], 1, 1, 1))
                        await state.finish()
                        await bot.send_message(chat_id=message.from_user.id, text="Сообщение отправилось заказчику.")
                    else:
                        await bot.send_message(chat_id=message.from_user.id, text="Вы указали прошедшую дату, напишите реальную дату начала выполнения заказ")
                except BaseException as err:
                    pass
                    await bot.send_message(chat_id=message.from_user.id, text="Неверный формат даты, напишите через dd.mm.yy или такой даты не существует")
            else:
                await bot.send_message(chat_id=message.from_user.id,
                                    text="Извините, неправильный тип сообщения, пожалуйста, ответьте текстом.")


        @dp.callback_query_handler(id_sender.filter(action="change_price_print"))
        async def change_price_print(call: types.CallbackQuery):
            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
            await bot.send_message(chat_id=genshin, text="Напишите цену числом.")
            await Print.final_price.set()


        @dp.message_handler(state=Print.final_price)
        async def final_price_print(message: types.Message, state: FSMContext):
            if message.text:
                if message.text.replace(' ', '').isdigit() and message.text != "0":
                    async with state.proxy() as data:
                        data["final_price"] = message.text
                        data["final_price"] = str(data["final_price"]).lstrip('0').replace(' ', '')
                    callback_data["price"] = data["final_price"]
                    await bot.send_message(chat_id=message.from_user.id, text='Вы подтверждаете введённую цену <b>{}</b>'.format(price_transformation(int(data["final_price"]))), reply_markup=keyboard_approve_price_print())
                    await state.finish()
                else:
                    await bot.send_message(chat_id=message.from_user.id, text="Напишите цену числом (также услуга не может быть бесплатной)")
            else:
                await bot.send_message(chat_id=message.from_user.id, text="Извините, неправильный тип сообщения, пожалуйста, ответьте текстом.")

        @dp.callback_query_handler(text="approve_price_print")
        async def approve_price_print(call: types.CallbackQuery):
            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
            await bot.send_message(chat_id=call.from_user.id, text="Клиенту направлено КП.")
            await bot.send_message(chat_id=callback_data["id_user"], text="Мы сможем приступить к Вашему заказу <b>{}</b>. Заказ будет стоить <b>{}</b>. Закончим работы <b>{}</b>".format(callback_data["begin"], price_transformation(int(callback_data["price"])), callback_data["time"]))
            await bot.send_message(chat_id=callback_data["id_user"], text="Выполнить для Вас заказ '{}'?\n".format(callback_data["project_name"]), reply_markup=keyboard_order_data_print(callback_data["id_user"], callback_data["project_name"], int(callback_data["price"]), 1, 1))

        @dp.callback_query_handler(text="disapprove_price_print")
        async def disapprove_price_print(call: types.CallbackQuery):
            await change_price_print(call)
    except BaseException as err:
        pass

@dp.callback_query_handler(id_sender.filter(action="suggest_print"))
async def suggest_print(call: types.CallbackQuery, callback_data: dict):
    try:
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await bot.send_message(chat_id=call.from_user.id, text="Исполнитель уже работает над заказом '{}', {}".format(callback_data["project_name"], text_suggest))
        #kirill
        await bot.send_message(chat_id=genshin, text="Заказчика устроили цена и сроки, как только выполните заказ, отправьте /end")
        await bot.send_message(chat_id=call.from_user.id, text=text_introduction, reply_markup=keyboard_1())

        @dp.message_handler(commands="end")
        async def project_name_print(message: types.Message):
            await bot.send_message(chat_id=message.from_user.id, text='Введите номер проекта!')
            await Print.end.set()

        @dp.message_handler(content_types=types.ContentTypes.ANY, state=Print.end)
        async def catch_name_print(message: types.Message, state: FSMContext):
            async with state.proxy() as data:
                data["end"] = message.text
            try:
                res = next(x[0] for x in db.print_project_names() if x[0]==data["end"])
                await bot.send_message(chat_id=message.from_user.id, text="Прикрепите скриншот выполненной работы")
                await Print.next()
            except StopIteration:
                await state.finish()
                await bot.send_message(chat_id=message.from_user.id, text='Такого номера проекта не существует, пожалуйста, введите корректный номер проекта')
                await project_name_print(message)

        @dp.message_handler(content_types=["photo"], state=Print.screenshot)
        async def send_screenshot_print(message: types.Message, state: FSMContext):
            if message.photo:
                async with state.proxy() as data:
                    data["screenshot"] = message.photo[0].file_id
                await bot.send_message(chat_id=message.from_user.id, text="Сообщение отправилось Заказчику с предложением об оплате.")
                await bot.send_photo(chat_id=callback_data["id_user"], photo=data["screenshot"], caption="Вам пришло фото в подтверждение выполненного заказа '{}'.\n".format(callback_data["project_name"]))
                await bot.send_message(chat_id=callback_data["id_user"], text="Готовы оплатить заказ '{}' на сумму {}?\nПосле оплаты вам прийдёт готовый проект.\n\nP.S. Если вы нажимаете нет, то вы отменяете заказ.".format(callback_data["project_name"], price_transformation(int(callback_data["price"]))), reply_markup=keyboard_payment_print())
                await state.finish()
            else:
                await bot.send_message(chat_id=message.from_user.id, text="Извините, неправильный тип сообщения, пожалуйста, пришлите фото.")

        @dp.callback_query_handler(text="payment_print")
        async def payment_print(call: types.CallbackQuery):
            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
            await bot.send_message(chat_id=call.from_user.id, text="Переведите {} по карте '{}' на имя Ганьшина В.К. и не забудьте сделать скриншот перевода.\n Как только произведёте оплату нажмите /pay".format(price_transformation(int(callback_data["price"])), number_of_card))

        @dp.message_handler(commands="pay")
        async def end_price_print(message: types.Message):
            await bot.send_message(chat_id=message.from_user.id, text='Пришлите чек об оплате')
            await Print.check.set()

        @dp.message_handler(content_types=["photo"], state=Print.check)
        async def check_print(message: types.Message, state: FSMContext):
            if message.photo:
                async with state.proxy() as data:
                    data["screenshot"] = message.message_id
                    await bot.send_message(chat_id=message.from_user.id, text='Пришлите свой номер')
                await Print.next()
            else:
                await bot.send_message(chat_id=message.from_user.id, text="Извините, неправильный тип сообщения, пожалуйста, пришлите фото.")
    except BaseException as err:
        pass


@dp.callback_query_handler(id_sender.filter(action="cancel_print"))
async def cancel_print(call: types.CallbackQuery, callback_data: dict):
    try:
        await bot.send_message(chat_id=call.from_user.id, text="Спасибо за обратную связь!")
        await bot.send_message(chat_id=call.from_user.id, text=text_introduction, reply_markup=keyboard_1())
    except BaseException as err:
        pass

# Хендлер под команду back_scan
@dp.callback_query_handler(state="*", text="back_print1")
async def revert_print(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        current_state = await state.get_state()
        if current_state is None:
            return
        await state.finish()
        await bot.send_message(chat_id=call.from_user.id, text=text_scan, reply_markup=keyboard_print())
    except BaseException as err:
        pass

# Хендлер под команду example
@dp.callback_query_handler(text="examples_print")
async def example_print1(call: types.CallbackQuery):
    try:
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        album = MediaGroup()
        album.attach_photo(photo=InputFile(path_or_bytesio='/home/Akveduk/bot/3d-print/project1/print1.jpg'), caption='Пример №1')
        album.attach_photo(photo=InputFile(path_or_bytesio='/home/Akveduk/bot/3d-print/project1/print2.jpg'))
        album.attach_photo(photo=InputFile(path_or_bytesio='/home/Akveduk/bot/3d-print/project1/print3.jpg'))
        album.attach_photo(photo=InputFile(path_or_bytesio='/home/Akveduk/bot/3d-print/project1/print4.jpg'))
        album.attach_photo(photo=InputFile(path_or_bytesio='/home/Akveduk/bot/3d-print/project1/print5.jpg'))
        album.attach_photo(photo=InputFile(path_or_bytesio='/home/Akveduk/bot/3d-print/project1/print6.jpg'))
        await call.message.answer_media_group(media=album)
        await call.message.answer('Больше фото проектов', reply_markup=keyboard_more_examples_print())
    except BaseException as err:
        pass

# # Handler for command example 2
@dp.callback_query_handler(text='more_print')
async def example_print2(call: types.CallbackQuery):
    try:
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        album = MediaGroup()
        album.attach_photo(photo=InputFile(path_or_bytesio='/home/Akveduk/bot/3d-print/project2/print1.jpg'), caption='Пример №2')
        album.attach_photo(photo=InputFile(path_or_bytesio='/home/Akveduk/bot/3d-print/project2/print2.jpg'))
        album.attach_photo(photo=InputFile(path_or_bytesio='/home/Akveduk/bot/3d-print/project2/print3.jpg'))
        album.attach_photo(photo=InputFile(path_or_bytesio='/home/Akveduk/bot/3d-print/project2/print4.jpg'))
        album.attach_photo(photo=InputFile(path_or_bytesio='/home/Akveduk/bot/3d-print/project2/print5.jpg'))
        await call.message.answer_media_group(media=album)
        await call.message.answer('Было представлено достаточно примеров для того, чтобы принять решение. Пора приступать к оценке стоимости своего проекта!', reply_markup=keyboard_after_print())
    except BaseException as err:
        pass

# Хендлер под команду back
@dp.callback_query_handler(text="back_print")
async def reset_print(call: types.CallbackQuery):
    try:
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await bot.send_message(chat_id=call.from_user.id, text=text_introduction, reply_markup=keyboard_1())
    except BaseException as err:
        pass

# Хендлер под команду back
@dp.callback_query_handler(text="back_cost_print")
async def back_cost_print(call: types.CallbackQuery):
    try:
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await bot.send_message(chat_id=call.from_user.id, text=text_introduction, reply_markup=keyboard_print())
    except BaseException as err:
        pass





























#<...3D-Modeling...>
#клавиатура под таблицу_2
def keyboard_model():
    buttons = [
        types.InlineKeyboardButton(text="Оценить стоимость", callback_data="file_model"),
        types.InlineKeyboardButton(text="Примеры проектов", callback_data="examples_model"),
        types.InlineKeyboardButton(text="Назад", callback_data="back_model")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


def keyboard_after_model():
    buttons = [
        types.InlineKeyboardButton(text="Назад", callback_data="back_model"),
        types.InlineKeyboardButton(text="Оценить стоимость", callback_data="file_model")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


# Клавиатура стоимости
def keyboard_file_model():
    buttons = [
        types.KeyboardButton(text="Назад"),
        types.KeyboardButton(text="Отправить задание на просчёт")
    ]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    keyboard.add(*buttons)
    return keyboard


# Keyboard for second example
def keyboard_more_examples_model():
    buttons = [
        types.InlineKeyboardButton(text='Назад', callback_data='back_cost_model'),
        types.InlineKeyboardButton(text="Ещё", callback_data="more_model")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(*buttons)
    return keyboard


# Keyboard for third example
def keyboard_more3_examples_model():
    buttons = [
        types.InlineKeyboardButton('Назад', callback_data='back_cost_model'),
        types.InlineKeyboardButton(text="Ещё", callback_data="more_model3")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(*buttons)
    return keyboard


# Клавиатура заказа
def keyboard_order_model(id_user, project_name, price, time, begin):
    buttons = [
        types.InlineKeyboardButton(text="Нет", callback_data=id_sender.new(action="no_model", id_user=id_user, project_name=project_name, price=price, time=time, begin=begin)),
        types.InlineKeyboardButton(text="Да", callback_data=id_sender.new(action="yes_model", id_user=id_user, project_name=project_name, price=price, time=time, begin=begin))
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


# Клавиатура подтверждения или отмены
def keyboard_order_data_model(id_user, project_name, price, time, begin):
    buttons = [
        types.InlineKeyboardButton(text="Нет", callback_data=id_sender.new(action="cancel_model", id_user=id_user, project_name=project_name, price=price, time=time, begin=begin)),
        types.InlineKeyboardButton(text="Да", callback_data=id_sender.new(action="suggest_model", id_user=id_user, project_name=project_name, price=price, time=time, begin=begin))
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


# Клавиатура стоимости
def keyboard_reason_model():
    buttons = [
        types.InlineKeyboardButton(text="Назад", callback_data="reason_model")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard

def keyboard_payment_model():
    buttons = [
        types.InlineKeyboardButton(text="Оплатить", callback_data="payment_model")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


def keyboard_change_price_model(id_user, project_name, price, time, begin):
    buttons = [
        types.InlineKeyboardButton(text="Изменить цену", callback_data=id_sender.new(action="change_price_model", id_user=id_user, project_name=project_name, price=price, time=time, begin=begin))
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard

def keyboard_approve_price_model():
    buttons = [
        types.InlineKeyboardButton(text="Нет", callback_data="disapprove_price_model"),
        types.InlineKeyboardButton(text="Да", callback_data="approve_price_model")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


# Хендлер под команду scan
@dp.callback_query_handler(text="model")
async def model(call: types.CallbackQuery):
    try:
        await bot.send_message(chat_id=call.from_user.id, text=text_model, reply_markup=keyboard_model())
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    except BaseException as err:
        pass

@dp.callback_query_handler(text="file_model")
async def cost_model(call: types.CallbackQuery):
    try:
        id_user_answer = call.from_user.id
        await bot.send_message(chat_id=call.from_user.id, text=text_count, reply_markup=keyboard_file_model())
        await Model.description.set()
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)


        @dp.message_handler(content_types=types.ContentTypes.ANY, state=Model.description)
        async def description(message: types.Message, state: FSMContext):
            now = datetime.now()
            number = random.randint(1,1000)
            if message.text == "Отправить задание на просчёт":
                if bd.messages_exist(message.from_user.id):
                    while 1:
                        project_name = 'M.{}.{}.{}'.format(now.day, now.month, number)
                        if not db.project_name_exists(project_name):
                            db.add_project_name(str(project_name))
                            break
                        else:
                            continue
                    #maksim
                    await bot.send_message(chat_id=genshin, text="<b>НОВЫЙ ЗАКАЗ</b> '{}'\n<b>Направление:</b> 3D-Моделирование".format(project_name))
                    #maksim
                    for i in bd.sent_messages(message.from_user.id):
                        for j in i:
                        #maksim
                            await bot.copy_message(chat_id=genshin, from_chat_id=message.from_user.id, message_id=j)
                    #maksim
                    await bot.send_message(chat_id=genshin, text="Есть вопросы по заказу?", reply_markup=keyboard_order_model(id_user_answer, project_name, 1, 1, 1))
                    await bot.send_message(chat_id=message.from_user.id, text="<b>Принято! Анализируем стоимость и сроки. Скоро ответим.</b>", reply_markup=types.ReplyKeyboardRemove())
                    await bot.send_message(chat_id=message.from_user.id, text=text_introduction, reply_markup=keyboard_1())
                    user = message.from_user.get_current()
                    #genshin
                    await bot.send_message(chat_id=genshin, text=f'\t<b>НОВАЯ ЗАЯВКА</b>\n\n<b>Номер заказа:</b> {project_name}\n\n<b>Имя Заказчика:</b> {user["first_name"]}\n\n<b>Фамилия Заказчика:</b> {user["last_name"]}\n\n<b>Никнейм Заказчика:</b> @{user["username"]}')
                    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
                    await state.finish()
                    bd.delete_messages(message.from_user.id)
                else:
                    await bot.send_message(chat_id=message.from_user.id, text='Пришлите описание проекта, исполнителю нужно чётко понимать задачу =)')

            if message.text == "Назад":
                current_state = await state.get_state()
                if current_state is None:
                    return
                await state.finish()
                await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
                await bot.send_message(chat_id=message.from_user.id, text='Назад', reply_markup=types.ReplyKeyboardRemove())
                await bot.send_message(chat_id=message.from_user.id, text=text_model, reply_markup=keyboard_model())
                bd.delete_messages(message.from_user.id)
            else:
                async with state.proxy() as data:
                    if message.text != "Отправить задание на просчёт" and message.text != 'Пришлите описание проекта, исполнителю нужно чётко понимать задачу =)':
                        data['description'] = message.message_id
                        bd.add_messages(message.from_user.id, data["description"])
    except BaseException as err:
        pass

# Хендлер под команде yes
@dp.callback_query_handler(id_sender.filter(action="yes_model"))
async def worker_yes_model(call: types.CallbackQuery, callback_data: dict):
    try:
        callback_data["id_user"] = call.from_user.id
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await bot.send_message(chat_id=call.from_user.id, text="Опишите свой вопрос")
        await Model.clarification.set()


        @dp.message_handler(state=Model.clarification)
        async def clarification_model(message: types.Message, state: FSMContext):
            async with state.proxy() as data:
                data['clarification'] = message.text
            await bot.send_message(chat_id=callback_data["id_user"], text="{} '{}'".format(text_clarification, callback_data["project_name"]) + "\n<b>Направление: </b> 3D-Моделирование" + '\n<b>Уточнение: </b>' + data["clarification"] + '\nДля ответа нажмите /answer')
            await state.finish()
            await message.reply("Вопрос отправился заказчику, ожидайте ответа")


        @dp.message_handler(commands="answer")
        async def preset_answer_model(message: types.Message):
            await bot.send_message(chat_id=message.from_user.id, text="Напишите ответ на вопрос исполнителя")
            await Model.answer.set()


        @dp.message_handler(state=Model.answer)
        async def answer_model(message: types.Message, state: FSMContext):
            async with state.proxy() as data:
                data["answer"] = message.text
            #maksim
            await bot.send_message(chat_id=genshin, text="Есть вопрос по заказу '{}'".format(callback_data["project_name"]) + "?\n" + data["answer"], reply_markup=keyboard_order_model(message.from_user.id, callback_data["project_name"], 1, 1, 1))
            await message.reply("Ответ отправился исполнителю, ожидайте реакции")
            await state.finish()
    except BaseException as err:
        pass

# Хендлер под команду no
@dp.callback_query_handler(id_sender.filter(action="no_model"))
async def worker_no_model(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    try:
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await bot.send_message(chat_id=call.from_user.id, text=worker_answer_price)
        await Model.id.set()
        await state.update_data(id=int(callback_data["id_user"]))
        await Model.next()
        await state.update_data(clarification=1)
        await Model.next()


        @dp.message_handler(state=Model.price)
        async def price_model(message: types.Message, state: FSMContext):
            if message.text:
                if message.text.replace(' ', '').isdigit() and message.text != "0":
                    async with state.proxy() as data:
                        data['price_Model'] = message.text
                        data["price_Model"] = str(data["price_Model"]).lstrip('0').replace(' ', '')
                    await message.reply(text=worker_answer_date)
                    await Model.next()
                else:
                    await bot.send_message(chat_id=message.from_user.id, text="Напишите цену числом (также услуга не может быть бесплатной)")
            else:
                await bot.send_message(chat_id=message.from_user.id, text="Извините, неправильный тип сообщения, пожалуйста, ответьте текстом.")


        @dp.message_handler(state=Model.date)
        async def date_model(message: types.Message, state: FSMContext):
            if message.text:
                if message.text.replace(' ', '').isdigit() and message.text != "0":
                    async with state.proxy() as data:
                        data['date_Model'] = message.text
                        data["date_Model"] = str(data["date_Model"]).lstrip('0')
                    await message.reply(text=worker_answer_start)
                    await Model.next()
                else:
                    await bot.send_message(chat_id=message.from_user.id, text="Напишите количество дней числом.")
            else:
                await bot.send_message(chat_id=message.from_user.id, text="Извините, неправильный тип сообщения, пожалуйста, ответьте текстом.")


        @dp.message_handler(state=Model.start)
        async def start_model(message: types.Message, state: FSMContext):
            if message.text:
                try:
                    if datetime.strptime(datetime.now().strftime("%d.%m.%y"), '%d.%m.%y').date() <= datetime.strptime(message.text, '%d.%m.%y').date():
                        async with state.proxy() as data:
                            data['start_Model'] = message.text
                        callback_data["time"] = data["date_Model"]
                        callback_data["begin"] = data["start_Model"]
                        callback_data["time"] = (datetime.strptime(callback_data["begin"], '%d.%m.%y') + timedelta(days=int(data["date_Model"]))).strftime('%d.%m.%y')
                        #maksim
                        await bot.send_message(chat_id=genshin, text="<b>Номер заказа:</b> '{}'\n<b>Направление:</b> 3D-Моделирование\n<b>Цена заказа:</b> {} \n<b>Количество дней выполнения:</b> {} \n<b>Начало выполнения:</b> {} \n<b>Конец выполнения:</b> {}".format(callback_data["project_name"], price_transformation(int(data["price_Model"])), date_transformation(int(data["date_Model"])), data["start_Model"], callback_data["time"]))
                        #maksim
                        await bot.send_message(chat_id=genshin, text="Укажите цену заказа '{}', нажав кнопку изменить цену\n".format(callback_data["project_name"]), reply_markup=keyboard_change_price_model(data["id"], callback_data["project_name"], 1, 1, 1))
                        await state.finish()
                        await bot.send_message(chat_id=message.from_user.id, text="Сообщение отправилось заказчику.")
                    else:
                        await bot.send_message(chat_id=message.from_user.id, text="Вы указали прошедшую дату, напишите реальную дату начала выполнения заказ")
                except BaseException as err:
                    pass
                    await bot.send_message(chat_id=message.from_user.id, text="Неверный формат даты, напишите через dd.mm.yy или такой даты не существует")
            else:
                await bot.send_message(chat_id=message.from_user.id, text="Извините, неправильный тип сообщения, пожалуйста, ответьте текстом.")


        @dp.callback_query_handler(id_sender.filter(action="change_price_model"))
        async def change_price_model(call: types.CallbackQuery):
            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
            await bot.send_message(chat_id=genshin, text="Напишите цену числом.")
            await Model.final_price.set()

        @dp.message_handler(state=Model.final_price)
        async def final_price_model(message: types.Message, state: FSMContext):
            if message.text:
                if message.text.replace(' ', '').isdigit() and message.text != "0":
                    async with state.proxy() as data:
                        data["final_price"] = message.text
                        data["final_price"] = str(data["final_price"]).lstrip('0').replace(' ', '')
                    callback_data["price"] = data["final_price"]
                    await bot.send_message(chat_id=message.from_user.id, text='Вы подтверждаете введённую цену <b>{}</b>'.format(price_transformation(int(data["final_price"]))), reply_markup=keyboard_approve_price_model())
                    await state.finish()
                else:
                    await bot.send_message(chat_id=message.from_user.id, text="Напишите цену числом (также услуга не может быть бесплатной)")
            else:
                await bot.send_message(chat_id=message.from_user.id, text="Извините, неправильный тип сообщения, пожалуйста, ответьте текстом.")

        @dp.callback_query_handler(text="approve_price_model")
        async def approve_price_model(call: types.CallbackQuery):
            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
            await bot.send_message(chat_id=call.from_user.id, text="Клиенту направлено КП.")
            await bot.send_message(chat_id=callback_data["id_user"], text="Мы сможем приступить к Вашему заказу <b>{}</b>. Заказ будет стоить <b>{}</b>. Закончим работы <b>{}</b>".format(callback_data["begin"], price_transformation(int(callback_data["price"])), callback_data["time"]))
            await bot.send_message(chat_id=callback_data["id_user"], text="Выполнить для Вас заказ '{}'?\n".format(callback_data["project_name"]), reply_markup=keyboard_order_data_model(callback_data["id_user"], callback_data["project_name"], int(callback_data["price"]), 1, 1))

        @dp.callback_query_handler(text="disapprove_price_model")
        async def disapprove_price_model(call: types.CallbackQuery):
            await change_price_model(call)
    except BaseException as err:
        pass


@dp.callback_query_handler(id_sender.filter(action="suggest_model"))
async def suggest_model(call: types.CallbackQuery, callback_data: dict):
    try:
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await bot.send_message(chat_id=call.from_user.id, text="Исполнитель уже работает над заказом '{}', {}".format(callback_data["project_name"], text_suggest))
        #maksim
        await bot.send_message(chat_id=genshin, text="Заказчика устроили цена и сроки, как только выполните заказ, отправьте /end")
        await bot.send_message(chat_id=call.from_user.id, text=text_introduction, reply_markup=keyboard_1())

        @dp.message_handler(commands="end")
        async def project_name_model(message: types.Message):
            await bot.send_message(chat_id=message.from_user.id, text='Введите номер проекта!')
            await Model.end.set()

        @dp.message_handler(content_types=types.ContentTypes.ANY, state=Model.end)
        async def catch_name_model(message: types.Message, state: FSMContext):
            async with state.proxy() as data:
                data["end"] = message.text
            try:
                res = next(x[0] for x in db.print_project_names() if x[0]==data["end"])
                await bot.send_message(chat_id=message.from_user.id, text="Прикрепите скриншот выполненной работы")
                await Model.next()
            except StopIteration:
                await state.finish()
                await bot.send_message(chat_id=message.from_user.id, text='Такого номер проекта не существует, пожалуйста, введите корректный номер проекта')
                await project_name_model(message)

        @dp.message_handler(content_types=["photo"], state=Model.screenshot)
        async def send_screenshot_model(message: types.Message, state: FSMContext):
            if message.photo:
                async with state.proxy() as data:
                    data["screenshot"] = message.photo[0].file_id
                await bot.send_message(chat_id=message.from_user.id, text="Сообщение отправилось Заказчику с предложением об оплате.")
                await bot.send_photo(chat_id=callback_data["id_user"], photo=data["screenshot"], caption="Вам пришло фото в подтверждение выполненного заказа '{}'.\n".format(callback_data["project_name"]))
                await bot.send_message(chat_id=callback_data["id_user"], text="Готовы оплатить заказ '{}' на сумму {}?\nПосле оплаты вам прийдёт готовый проект.".format(callback_data["project_name"], price_transformation(int(callback_data["price"]))), reply_markup=keyboard_payment_model())
                await state.finish()
            else:
                await bot.send_message(chat_id=message.from_user.id, text="Извините, неправильный тип сообщения, пожалуйста, пришлите фото.")

        @dp.callback_query_handler(text="payment_model")
        async def payment_model(call: types.CallbackQuery):
            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
            await bot.send_message(chat_id=call.from_user.id, text="Переведите {} по карте '{}' на имя Ганьшина В.К. и не забудьте сделать скриншот перевода.\n Как только произведёте оплату нажмите /pay".format(price_transformation(int(callback_data["price"])), number_of_card))

        @dp.message_handler(commands="pay")
        async def end_price_model(message: types.Message):
            await bot.send_message(chat_id=message.from_user.id, text='Пришлите чек об оплате')
            await Model.check.set()

        @dp.message_handler(content_types=["photo"], state=Model.check)
        async def check_model(message: types.Message, state: FSMContext):
            if message.photo:
                async with state.proxy() as data:
                    data["screenshot"] = message.message_id
                    await bot.send_message(chat_id=message.from_user.id, text='Пришлите свой номер')
                await Model.next()
            else:
                await bot.send_message(chat_id=message.from_user.id, text="Извините, неправильный тип сообщения, пожалуйста, пришлите фото.")
    except BaseException as err:
        pass


@dp.callback_query_handler(id_sender.filter(action="cancel_model"))
async def cancel_model(call: types.CallbackQuery, callback_data: dict):
    try:
        await bot.send_message(chat_id=call.from_user.id, text="Спасибо за обратную связь!")
        await bot.send_message(chat_id=call.from_user.id, text=text_introduction, reply_markup=keyboard_1())
    except BaseException as err:
        pass

# Хендлер под команду back_scan
@dp.callback_query_handler(state="*", text="back_model1")
async def revert_model(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        current_state = await state.get_state()
        if current_state is None:
            return
        await state.finish()
        await bot.send_message(chat_id=call.from_user.id, text=text_scan, reply_markup=keyboard_model())
    except BaseException as err:
        pass

# Хендлер под команду example
@dp.callback_query_handler(text="examples_model")
async def example_model1(call: types.CallbackQuery):
    try:
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        album = MediaGroup()
        album.attach_photo(photo=InputFile(path_or_bytesio='/home/Akveduk/bot/3d-model/project4/mod1.jpg'), caption='Пример №1')
        album.attach_photo(photo=InputFile(path_or_bytesio='/home/Akveduk/bot/3d-model/project4/mod2.jpg'))
        album.attach_photo(photo=InputFile(path_or_bytesio='/home/Akveduk/bot/3d-model/project4/mod3.jpg'))
        album.attach_photo(photo=InputFile(path_or_bytesio='/home/Akveduk/bot/3d-model/project4/mod4.jpg'))
        album.attach_photo(photo=InputFile(path_or_bytesio='/home/Akveduk/bot/3d-model/project4/mod5.jpg'))
        album.attach_photo(photo=InputFile(path_or_bytesio='/home/Akveduk/bot/3d-model/project4/mod6.jpg'))
        await call.message.answer_media_group(media=album)
        await call.message.answer('Больше фото проектов', reply_markup=keyboard_more_examples_model())
    except BaseException as err:
        pass

# # Handler for command example 2
@dp.callback_query_handler(text='more_model')
async def example_model2(call: types.CallbackQuery):
    try:
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        album = MediaGroup()
        album.attach_photo(photo=InputFile(path_or_bytesio='/home/Akveduk/bot/3d-model/project2/mod1.jpg'), caption='Пример №2')
        album.attach_photo(photo=InputFile(path_or_bytesio='/home/Akveduk/bot/3d-model/project2/mod2.jpg'))
        album.attach_photo(photo=InputFile(path_or_bytesio='/home/Akveduk/bot/3d-model/project2/mod3.jpg'))
        await call.message.answer_media_group(media=album)
        await call.message.answer('Больше фото проектов', reply_markup=keyboard_more3_examples_model())
    except BaseException as err:
        pass

# Handler for command example 3
@dp.callback_query_handler(text='more_model3')
async def example_model3(call: types.CallbackQuery):
    try:
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        album = MediaGroup()
        album.attach_photo(photo=InputFile(path_or_bytesio='/home/Akveduk/bot/3d-model/project1/mod1.jpg'), caption='Пример №3')
        album.attach_photo(photo=InputFile(path_or_bytesio='/home/Akveduk/bot/3d-model/project1/mod2.jpg'))
        album.attach_photo(photo=InputFile(path_or_bytesio='/home/Akveduk/bot/3d-model/project1/mod3.jpg'))
        await call.message.answer_media_group(media=album)
        await call.message.answer('Было представлено достаточно примеров для того, чтобы принять решение. Пора приступать к оценке стоимости своего проекта!', reply_markup=keyboard_after_model())
    except BaseException as err:
        pass


# Хендлер под команду back
@dp.callback_query_handler(text="back_model")
async def reset_model(call: types.CallbackQuery):
    try:
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await bot.send_message(chat_id=call.from_user.id, text=text_introduction, reply_markup=keyboard_1())
    except BaseException as err:
        pass

# Хендлер под команду back
@dp.callback_query_handler(text="back_cost_model")
async def back_cost_model(call: types.CallbackQuery):
    try:
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await bot.send_message(chat_id=call.from_user.id, text=text_introduction, reply_markup=keyboard_model())
    except BaseException as err:
        pass


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
