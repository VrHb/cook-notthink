import os
import json
from typing import NamedTuple

from dotenv import load_dotenv
from django.core.management.base import BaseCommand

from telegram import InlineKeyboardButton, ReplyKeyboardMarkup, \
    InlineKeyboardMarkup, parsemode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, \
    CallbackQueryHandler, ConversationHandler

from telegram_bot_pagination import InlineKeyboardPaginator

from foodplan.data_operations import get_dishes_from_json


AUTORIZATION, DISHES, ACCOUNT, MY_DISHES = range(4)

BUTTON_MY_DISHES = "Мои блюда"
BUTTON_CHOICE_DISH = "Выбрать блюдо"
BUTTON_BACK = "Назад"
BUTTON_APPROVE = "Согласен"
BUTTON_REJECT = "Отказываюсь"
BUTTON_ACCOUNT = "Личный кабинет"


user_in = {}

class Dish(NamedTuple):
    category: str
    title: str
    description: str
    ingridients: str
    image: str
    calories: str

class Command(BaseCommand):
    help = 'Телеграм бот'

    def handle(self, *args, **options):
        load_dotenv()
        updater = Updater(os.getenv("TELEGRAM_TOKEN"), use_context=True)
        dp = updater.dispatcher
        conv_handler = ConversationHandler(
            entry_points=[
                CommandHandler("start", autorization_handler),
                CallbackQueryHandler(
                    callback=callback_approve_handler,
                    pass_chat_data=True
                )
            ],
            states={
                DISHES:
                [
                    CommandHandler("account", callback=account_handler),
                    CallbackQueryHandler(
                        callback=dish_pages_callback,
                        pattern="^dishes",
                        pass_chat_data=True
                    ),
                ], 
                ACCOUNT:
                [
                    CommandHandler("account", callback=account_handler),
                    CallbackQueryHandler(
                        callback=dishes_pages_callback,
                        pattern="^dishes",
                        pass_chat_data=True
                    ),
                    CallbackQueryHandler(
                        callback=callback_dishes_handler,
                        pass_chat_data=True
                    )
                ]
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )
        dp.add_handler(conv_handler)
        updater.start_polling()

#  Add to data_operations module


all_dishes = get_dishes_from_json()
dishes = all_dishes[:100]
added_dishes = dishes[20:30]


def autorization_handler(update, context):
    user_id = update.message.from_user.id
    chat_id = update.effective_chat.id
    reply_markup = get_autorization_keyboard()
    message = "Соглашение на обработку пд"
    context.bot.send_message(
        chat_id=chat_id,
        text=message,
        reply_markup=reply_markup
    )


def account_handler(update, context):
    user_id = update.message.from_user.id
    chat_id = update.effective_chat.id
    reply_markup = get_user_keyboard()
    message = "Ваш личный кабинет"
    context.bot.send_photo(
        chat_id=chat_id,
        photo="https://foodplan.ru/lp/img/phone-top-banner.jpeg"
    )
    context.bot.send_message(
        chat_id=chat_id,
        text=message,
        reply_markup=reply_markup
    )
    return ACCOUNT


def callback_approve_handler(update, context):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    query = update.callback_query
    data = query.data
    print(user_id)
    if data == BUTTON_APPROVE: 
        user_in["telegram_id"] = user_id
        print(user_in)
    if data == BUTTON_REJECT:
        user_in["telegram_id"] = ""
        context.bot.send_message(
            chat_id=chat_id,
            text="Без соглашения на обработку мы не может оказать вам услугу"
        )
    if user_in["telegram_id"]:    
        message = "Блюда на выбор"
        context.bot.send_message(
            chat_id=chat_id,
            text=message,
        )
        paginator = InlineKeyboardPaginator(
            len(dishes),
            data_pattern="dishes#{page}",
        )
        paginator.add_before(
        InlineKeyboardButton('Хочу попробовать', callback_data='like#{}'),
            )

        paginator.add_after(
            InlineKeyboardButton('Личный кабинет', callback_data=BUTTON_ACCOUNT)
        )
        context.bot.send_message(
            chat_id=chat_id,
            text=f"*{dishes[0]['title']}*\n{dishes[0]['description']}\n{dishes[0]['imgs_url']}",
            reply_markup=paginator.markup,
            parse_mode="Markdown"
        )

        return DISHES 


def callback_dishes_handler(update, context):
    chat_id = update.effective_chat.id
    query = update.callback_query
    data = query.data
    if data == BUTTON_MY_DISHES:
        paginator = InlineKeyboardPaginator(
            len(added_dishes),
            data_pattern="dishes#{page}"
        )
        paginator.add_after(
            InlineKeyboardButton('Назад', callback_data=BUTTON_BACK)
        )
        context.bot.send_message(
            chat_id=chat_id,
            text=f"*{dishes[0]['title']}*\n{dishes[0]['description']}\n{dishes[0]['imgs_url']}",
            reply_markup=paginator.markup,
            parse_mode="Markdown"
        )
    if data == BUTTON_BACK:
        reply_markup = get_user_keyboard()
        message = "Ваш личный кабинет"
        context.bot.send_photo(
            chat_id=chat_id,
            photo="https://foodplan.ru/lp/img/phone-top-banner.jpeg"
        )
        context.bot.send_message(
            chat_id=chat_id,
            text=message,
            reply_markup=reply_markup
        )
    if data == BUTTON_CHOICE_DISH:
        context.bot.send_message(
            chat_id=chat_id,
            text="Меню выбора блюд"
        )


def dish_pages_callback(update, context):
    query = update.callback_query
    chat_id = update.effective_chat.id
    data = query.data
    query.answer()
    print(query)
    page = int(query.data.split('#')[1])
    reply_markup = get_user_keyboard()
    paginator = InlineKeyboardPaginator(
        len(dishes),
        current_page=page,
        data_pattern='dishes#{page}'
    )
    paginator.add_before(
        InlineKeyboardButton('Хочу попробовать', callback_data='like'),
    )
    paginator.add_after(
        InlineKeyboardButton('Личный кабинет', callback_data=BUTTON_ACCOUNT)
    )
    query.edit_message_text(
        text=f"*{dishes[page - 1]['title']}*\n{dishes[page -1]['description']}\n{dishes[page -1]['imgs_url']}",
        reply_markup=paginator.markup,
        parse_mode="Markdown"
    )
    print(data)
    if data == BUTTON_ACCOUNT:
        reply_markup = get_user_keyboard()
        message = "Ваш личный кабинет"
        context.bot.send_photo(
            chat_id=chat_id,
            photo="https://foodplan.ru/lp/img/phone-top-banner.jpeg"
        )
        context.bot.send_message(
            chat_id=chat_id,
            text=message,
            reply_markup=reply_markup
        )
        return ACCOUNT


def dishes_pages_callback(update, context):
    query = update.callback_query
    query.answer()
    page = int(query.data.split('#')[1])
    paginator = InlineKeyboardPaginator(
        len(added_dishes),
        current_page=page,
        data_pattern='dishes#{page}'
    )
    paginator.add_after(
        InlineKeyboardButton('Назад', callback_data=BUTTON_BACK)
    )
    query.edit_message_text(
        text=f"*{dishes[page - 1]['title']}*\n{dishes[page -1]['description']}\n{dishes[page -1]['imgs_url']}",
        reply_markup=paginator.markup,
        parse_mode="Markdown"
    )


def cancel(update, context):
    user = update.message.from_user
    update.message.reply_text(
        "вы вышли"
    )
    return ConversationHandler.END


def get_user_keyboard():
    keyboard=[
        [InlineKeyboardButton("Мои блюда", callback_data=BUTTON_MY_DISHES)],
        [InlineKeyboardButton("Добавить блюдо", callback_data=BUTTON_CHOICE_DISH)],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_autorization_keyboard():
    keyboard=[
        [InlineKeyboardButton("Принимаю", callback_data=BUTTON_APPROVE)],
        [InlineKeyboardButton("Отказываюсь", callback_data=BUTTON_REJECT)],
    ]
    return InlineKeyboardMarkup(keyboard)

