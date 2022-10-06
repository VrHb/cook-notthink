import os

from dotenv import load_dotenv
from django.core.management.base import BaseCommand

from telegram import InlineKeyboardButton, ReplyKeyboardMarkup, \
    InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, \
    CallbackQueryHandler, ConversationHandler

from telegram_bot_pagination import InlineKeyboardPaginator


AUTORIZATION, USER_LK, MY_DISHES = range(3)

BUTTON_MY_DISHES = "Мои блюда"
BUTTON_CHOICE_DISH = "Выбрать блюдо"
BUTTON_BACK = "Назад"
BUTTON_APPROVE = "Согласен"
BUTTON_REJECT = "Отказываюсь"


print(AUTORIZATION)

user_in = {}
print(bool(user_in.get("telegram_id")))


added_dishes = [
    "Вареники с творогом", 
    "Тыквенный суп с беконом", 
    "Праздничная свинина «Гармошка»", 
    "Наггетсы из грудки на сковороде", 
    "Куриная грудка с овощами на сковороде", 
    "Минтай в кляре"
]

# добавить json с картинками и описанием блюд

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
                USER_LK:
                [
                    CallbackQueryHandler(
                        callback=dishes_pages_callback,
                        pattern="^dishes"
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
        return USER_LK


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
            text=added_dishes[0],
            reply_markup=paginator.markup,
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
        text=added_dishes[page - 1],
        reply_markup=paginator.markup,
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

