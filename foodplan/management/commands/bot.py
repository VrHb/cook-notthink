import os

from dotenv import load_dotenv
from django.core.management.base import BaseCommand

from telegram import InlineKeyboardButton, ReplyKeyboardMarkup, \
    InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, \
    CallbackQueryHandler



BUTTON_MY_DISHES = "Мои блюда"
BUTTON_CHOICE_DISH = "Выбрать блюдо"

BUTTON_RISE = "Рисовая каша"
BUTTON_BREAD = "Хлеб"
BUTTON_OMELETTE = "Амлет"


class Command(BaseCommand):
    help = 'Телеграм бот'

    def handle(self, *args, **options):
        load_dotenv()
        updater = Updater(os.getenv("TELEGRAM_TOKEN"), use_context=True)
        dp = updater.dispatcher
        dp.add_handler(CommandHandler("start", start_handler))
        dp.add_handler(
            CallbackQueryHandler(
                callback=callback_dishes_handler,
                pass_chat_data=True
            )
        )
        updater.start_polling()


def start_handler(update, context):
    chat_id = update.effective_chat.id
    reply_markup = get_user_keyboard()
    message = "Ваш личный кабинет"
    context.bot.send_photo(
        chat_id=chat_id,
        photo="https://cdn4.vectorstock.com/i/1000x1000/51/68/eat-vector-21865168.jpg"
    )
    context.bot.send_message(
        chat_id=chat_id,
        text=message,
        reply_markup=reply_markup
    )


def callback_dishes_handler(update, context):
    chat_id = update.effective_chat.id
    query = update.callback_query
    data = query.data
    if data == BUTTON_MY_DISHES:
        reply_markup = get_dishes_keyboard()
        context.bot.send_message(
            chat_id=chat_id,
            text="Блюда на сегодняшний день",
            reply_markup=reply_markup
        )
    if data == BUTTON_CHOICE_DISH:
        context.bot.send_message(
            chat_id=chat_id,
            text="Меню выбора блюд"
        )


def get_user_keyboard():
    keyboard=[
        [InlineKeyboardButton("Мои блюда", callback_data=BUTTON_MY_DISHES)],
        [InlineKeyboardButton("Добавить блюдо", callback_data=BUTTON_CHOICE_DISH)],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_dishes_keyboard():
    keyboard=[
        [InlineKeyboardButton("Амлет", callback_data=BUTTON_OMELETTE)],
        [InlineKeyboardButton("Рисовая каша", callback_data=BUTTON_RISE)],
        [InlineKeyboardButton("Ржаной хлеб", callback_data=BUTTON_BREAD)],
    ]
    return InlineKeyboardMarkup(keyboard)

