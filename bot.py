import config
import db
import asyncio
import feedparser
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.contrib.fsm_storage.memory import MemoryStorage


loop = asyncio.get_event_loop()
storage = MemoryStorage()

bot = Bot(token=config.token, loop=loop)
dp = Dispatcher(bot, storage=storage)


# States
FILTER_BY = ''
URL = ''
JOB_ID = ''


base_category_url = 'https://admin10.rabota.ua/Export/Vacancy/feed.ashx?parentId='
base_region_url = 'https://admin10.rabota.ua/Export/Vacancy/feed.ashx?regionId='

category = {'HR специалисты - Бизнес-тренеры': 3,
            'IT': 1,
            'Автобизнес - Сервисное обслуживание': 33,
            'Админ. персонал - Водители - Курьеры': 11,
            'Банки - Инвестиции - Лизинг': 18,
            'Бухгалтерия - Налоги - Финансы предприятия' : 6,
            'Гостиницы - Рестораны - Кафе': 8,
            'Гос. учреждения - Местное самоуправление': 34,
            'Дизайн - Графика - Фото': 15,
            'Закупки - Снабжение': 31,
            'Консалтинг - Аналитика - Аудит': 14,
            'Культура - Шоу-бизнес - Развлечения': 21,
            'Логистика - Таможня - Склад': 5,
            'Маркетинг - Реклама - PR': 24,
            'Медиа - Издательское дело': 22,
            'Медицина - Фармацевтика - Здравоохранение': 9,
            'Морские специальности': 25,
            'Наука - Образование - Перевод': 10,
            'Недвижимость': 28,
            'Некоммерческие - Общественные организации':13,
            'Охрана - Безопасность - Силовые структуры': 4,
            'Продажи - Клиент-менеджмент': 17,
            'Производство - Инженеры - Технологи': 32,
            'Рабочие специальности - Персонал для дома': 20,
            'Сельское хозяйство - Агробизнес - Лесное хозяйство': 26,
            'Спорт - Красота - Оздоровление': 7,
            'Страхование': 19,
            'Строительство - Архитектура': 27,
            'Студенты - Начало карьеры - Без опыта': 30,
            'Телекоммуникации - Связь': 2,
            'Топ-менеджмент - Директора': 12,
            'Торговля': 16,
            'Туризм - Путешествия': 23,
            'Юристы, адвокаты, нотариусы': 29
}

region = {'Белая Церковь': 215,
          'Борисполь': 218,
          'Бровары': 221,
          'Винница': 5,
          'Вишневое': 571,
          'Днепр': 4,
          'Другие страны': 34,
          'Житомир': 7,
          'Закарпатье': 8,
          'Запорожье': 9,
          'Ивано-Франковск': 10,
          'Ирпень': 229,
          'Каменское': 82,
          'Киев': 1,
          'Краматорск': 121,
          'Кременчуг': 35,
          'Кривой Рог': 31,
          'Кропивницкий': 11,
          'Луцк': 14,
          'Львов': 2,
          'Мариуполь': 27,
          'Николаев': 15,
          'Одесса': 3,
          'Полтава': 17,
          'Ровно': 18,
          'Сумы': 19,
          'Тернополь': 20,
          'Ужгород': 28,
          'Харьков': 21,
          'Херсон': 22,
          'Хмельницкий': 23,
          'Черкассы': 24,
          'Чернигов': 25,
          'Черновцы': 26


}

@dp.message_handler(func=lambda c: True)
@dp.message_handler(commands=['start'])
async def start_process(msg: types.Message):

    keyboard = types.InlineKeyboardMarkup()
    category_btn = types.InlineKeyboardButton(text='💼 По категориям', callback_data='category')
    region_btn = types.InlineKeyboardButton(text='🇺🇦 По регионам', callback_data='region')
    keyboard.add(category_btn)
    keyboard.insert(region_btn)

    try:
        if msg.data == 'start':

            await bot.edit_message_reply_markup(msg.message.chat.id, msg.message.message_id, reply_markup=keyboard)
    except AttributeError:

        await bot.send_message(msg.chat.id, '🔎 Будем искать работу 🔎', reply_markup=keyboard)



@dp.callback_query_handler(func=lambda c: c.data == 'category')
async def category_process(callback: types.InlineQuery):

    await storage.update_data(chat=callback.message.chat.id, user=callback.message.from_user.id, filter_by=callback.data)

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(*[types.InlineKeyboardButton(text=i, callback_data=category[i]) for i in category])
    keyboard.add(types.InlineKeyboardButton(text='↩️ В главное меню', callback_data='start'))
    await bot.edit_message_reply_markup(callback.message.chat.id, callback.message.message_id, reply_markup=keyboard)

@dp.callback_query_handler(func=lambda c: c.data == 'region')
async def region_process(callback):

    await storage.update_data(chat=callback.message.chat.id, user=callback.message.from_user.id,
                              filter_by=callback.data)

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(*[types.InlineKeyboardButton(text=i, callback_data=region[i]) for i in region])
    keyboard.add(types.InlineKeyboardButton(text='↩️ В главное меню', callback_data='start'))

    await bot.edit_message_reply_markup(callback.message.chat.id, callback.message.message_id, reply_markup=keyboard)


@dp.callback_query_handler(func= lambda c: c.data.isdigit())
async def url_process(callback):

    with dp.current_state(chat=callback.message.chat.id, user=callback.message.from_user.id) as state:

        await state.update_data(url=callback.data)
        data = await state.get_data()



    if data['filter_by'] == 'category':
        msg = [k for k,v in category.items() if v == int(data['url'])]
        link = base_category_url + callback.data
    elif data['filter_by'] == 'region':
        msg = [k for k, v in region.items() if v == int(data['url'])]
        link = base_region_url + callback.data

    d = feedparser.parse(link)
    job = d.entries[0]
    data['job_id'] = job.id

    user = db.session.query(db.User).filter_by(user_id=callback.message.chat.id).first()
    if user:
        user.data = data
        db.session.commit()
    else:
        user = db.User(user_id=callback.message.chat.id, data=data)
        db.session.add(user)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            await bot.send_message(callback.message.chat.id, 'Сервис временно не доступен...')

    await bot.edit_message_reply_markup(callback.message.chat.id, callback.message.message_id)
    await bot.send_message(callback.message.chat.id, 'Вы выбрали {}\nПоследнее объявление:\n{}'.format(msg[0], job.id))


@dp.callback_query_handler(func= lambda c: c.data == 'start')
async def back(callback):
    await start_process(callback)


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()
    db.session.close_all()


async def sched():
    for user in db.session.query(db.User).all():

        if user.data['filter_by'] == 'category':
            link = base_category_url + user.data['url']
        elif user.data['filter_by'] == 'region':
            link = base_region_url + user.data['url']

        d = feedparser.parse(link)
        job = d.entries[0]

        if user.data['job_id'] != job.id:

            user.data['job_id'] = job.id
            db.session.commit()
            await bot.send_message(user.user_id, job.id)


scheduler = AsyncIOScheduler()
scheduler.add_job(sched, 'interval', seconds=60)
scheduler.start()


if __name__ == '__main__':
    executor.start_polling(dp, loop=loop, skip_updates=True, on_shutdown=shutdown)
