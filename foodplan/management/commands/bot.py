import os
import random

from dotenv import load_dotenv
from django.core.management.base import BaseCommand

from telegram import InlineKeyboardButton, ReplyKeyboardMarkup, \
    InlineKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, \
    CallbackQueryHandler, ConversationHandler

from telegram_bot_pagination import InlineKeyboardPaginator

from loguru import logger

from foodplan.data_operations import get_dishes_from_json, is_new_user, save_user_data, validate_fullname, validate_phonenumber


logger.debug("console log")

AUTORIZATION, DISHES, ACCOUNT, MY_DISHES = range(4)

BUTTON_MY_DISHES = "Мои блюда"
BUTTON_CHOICE_DISH = "Выбрать блюдо"
BUTTON_BACK = "Назад"
BUTTON_APPROVE = "Согласен"
BUTTON_REJECT = "Отказываюсь"
BUTTON_ACCOUNT = "Личный кабинет"
BUTTON_LIKE = "Хочу попробовать"
BUTTON_NO = "Другое блюдо"
BUTTON_IGNORE = "Больше не показывать"
BUTTON_END = "Выход"


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
                    pass_chat_data=True,
                )
            ],
            states={
                AUTORIZATION:
                [
                CallbackQueryHandler(
                    callback=callback_approve_handler,
                    pass_chat_data=True
                ),
                MessageHandler(Filters.text, get_phone),
                MessageHandler(Filters.contact, get_dish),
                ],
                DISHES:
                [
                    CommandHandler("account", callback=account_handler),
                    CallbackQueryHandler(
                        callback=dish_pages_callback,
                        pass_chat_data=True
                    ),
                ], 
                ACCOUNT:
                [
                    CommandHandler("account", callback=account_handler),
                    CallbackQueryHandler(
                        callback=dishes_account_callback,
                        pattern="^dishes",
                        pass_chat_data=True
                    ),
                    CallbackQueryHandler(
                        callback=callback_account_handler,
                        pass_chat_data=True,
                    )
                ]
            },
            fallbacks=[CommandHandler('cancel', cancel)],
        )
        dp.add_handler(conv_handler)
        updater.start_polling()


all_dishes = get_dishes_from_json()
dishes = all_dishes[:100]
added_dishes = dishes[20:30]
user_in = {}
choised_dishes = []
get_name = False 


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
    return AUTORIZATION


def account_handler(update, context):
    user_id = update.message.from_user.id
    chat_id = update.effective_chat.id
    reply_markup = get_user_keyboard()
    message = "https://foodplan.ru/lp/img/phone-top-banner.jpeg\n*Ваш личный кабинет*"
    context.bot.send_message(
        chat_id=chat_id,
        text=message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return ACCOUNT


def callback_approve_handler(update, context):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    query = update.callback_query
    data = query.data
    logger.info(user_id)
    if data == BUTTON_APPROVE:
        user_in["telegram_id"] = user_id
        context.bot.send_message(
            chat_id=chat_id,
            text="Введите имя и фамилию"
        )
        get_name = True
        print(user_in)
        return AUTORIZATION
    if data == BUTTON_REJECT:
        user_in["telegram_id"] = ""
        context.bot.send_message(
            chat_id=chat_id,
            text="Без соглашения на обработку мы не можем оказать вам услугу"
        )
        return conversation.END
    if user_in["telegram_id"]:
        dish = random.choice(dishes)
        context.bot.send_message(
                chat_id=chat_id,
            text=f"*{dish['title']}*\n{dish['description']}\n{dish['imgs_url']}",
            reply_markup=get_disheschoise_keyboard(),
            parse_mode="Markdown"
        )
        return DISHES 


def get_dish(update, context):
    user_data = context.user_data
    logger.info(user_data)
    user_id = update.message.from_user.id
    chat_id = update.effective_chat.id
    dish = random.choice(dishes)
    context.bot.send_message(
        chat_id=chat_id,
        text=f"*{dish['title']}*\n{dish['description']}\n{dish['imgs_url']}",
        reply_markup=get_disheschoise_keyboard(),
        parse_mode="Markdown"
    )
    return DISHES 


def get_phone(update, context):
    user_id = update.message.from_user.id
    chat_id = update.effective_chat.id
    message_keyboard = [[KeyboardButton("Отправить свой номер телефона", request_contact=True)]]
    markup = ReplyKeyboardMarkup(message_keyboard, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text(f"Введите телефон в формате +7... или нажав на кнопку ниже:", reply_markup=markup)


def callback_account_handler(update, context):
    chat_id = update.effective_chat.id
    query = update.callback_query
    data = query.data
    if data == BUTTON_MY_DISHES:
        paginator = InlineKeyboardPaginator(
            len(choised_dishes),
            data_pattern="dishes#{page}"
        )
        paginator.add_after(
            InlineKeyboardButton('Назад', callback_data=BUTTON_BACK)
        )
        context.bot.send_message(
            chat_id=chat_id,
            text=f"*{choised_dishes[0]['title']}*\n{choised_dishes[0]['description']}\n{choised_dishes[0]['imgs_url']}",
            reply_markup=paginator.markup,
            parse_mode="Markdown"
        )
    if data == BUTTON_BACK:
        reply_markup = get_user_keyboard()
        message = "https://foodplan.ru/lp/img/phone-top-banner.jpeg\n*Ваш личный кабинет*"
        context.bot.send_message(
            chat_id=chat_id,
            text=message,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    if data == BUTTON_CHOICE_DISH:
        dish = random.choice(dishes) 
        context.bot.send_message(
            chat_id=chat_id,
            text=f"*{dish['title']}*\n{dish['description']}\n{dish['imgs_url']}",
            reply_markup=get_disheschoise_keyboard(),
            parse_mode="Markdown"
        )
        return DISHES

@logger.catch
def dish_pages_callback(update, context):
    dish = random.choice(dishes)
    query = update.callback_query
    data = query.data
    chat_id = update.effective_chat.id
    data = query.data
    if data == BUTTON_LIKE:
        choised_dishes.append(dish)
    message = f"*{dish['title']}*\n{dish['description']}\n{dish['imgs_url']}"
    logger.info(dish["title"])
    context.bot.send_message(
        chat_id=chat_id,
        reply_markup=get_disheschoise_keyboard(),
        text=message,
        parse_mode="Markdown"
    )
    if data == BUTTON_IGNORE:
        context.bot.send_message(
            chat_id=chat_id,
            text="ОК, это блюдо больше не рекомдуем",
            parse_mode="Markdown"
        )
    if data == BUTTON_END:
        context.bot.delete_message(
            chat_id=chat_id,
            message_id=message.message_id
            )
        return cancel 
    logger.info(context.user_data)
    logger.info(data)
    logger.info(choised_dishes)


def dishes_account_callback(update, context):
    query = update.callback_query
    query.answer()
    page = int(query.data.split('#')[1])
    paginator = InlineKeyboardPaginator(
        len(choised_dishes),
        current_page=page,
        data_pattern='dishes#{page}'
    )
    paginator.add_after(
        InlineKeyboardButton('Назад', callback_data=BUTTON_BACK)
    )
    query.edit_message_text(
        text=f"*{choised_dishes[page - 1]['title']}*\n{choised_dishes[page -1]['description']}\n{choised_dishes[page -1]['imgs_url']}",
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


def get_disheschoise_keyboard():
    keyboard=[
        [InlineKeyboardButton("Хочу попробовать", callback_data=BUTTON_LIKE)],
        [InlineKeyboardButton("Другое блюдо", callback_data=BUTTON_NO)],
        [InlineKeyboardButton("Больше не показывать", callback_data=BUTTON_IGNORE)],
        [InlineKeyboardButton("Выход", callback_data=BUTTON_END)],
    ]
    return InlineKeyboardMarkup(keyboard)

