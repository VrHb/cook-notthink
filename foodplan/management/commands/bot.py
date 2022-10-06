import os

import phonenumbers
from dotenv import load_dotenv
from django.core.management.base import BaseCommand
from telegram import ReplyKeyboardMarkup, KeyboardButton


from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler
)
from foodplan.common_functions import is_new_user, save_user_data, validate_fullname, validate_phonenumber

USER_FULLNAME, PHONE_NUMBER, END_AUTH, PERSONAL_ACCOUNT = range(4)


class Command(BaseCommand):
    help = "Телеграм бот"

    def handle(self, *args, **options):
        load_dotenv()
        updater = Updater(os.getenv("TELEGRAM_TOKEN"), use_context=True)
        dp = updater.dispatcher

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", start)],
            states={
                USER_FULLNAME: [
                    MessageHandler(
                        Filters.regex('^(✅ Согласен)$'), get_fullname
                    ),
                ],
                PHONE_NUMBER: [
                    MessageHandler(Filters.text, get_phonenumber)],
                END_AUTH: [
                    MessageHandler(Filters.text, end_auth),
                    MessageHandler(Filters.contact, end_auth),
                ],
                PERSONAL_ACCOUNT: [
                    MessageHandler(Filters.regex('^(Получение рецептов)$'),
                                   create_order),
                    MessageHandler(Filters.regex('^(Личный кабинет)$'),
                                   personal_account)
                ],
            },
            fallbacks=[MessageHandler(Filters.regex("^Стоп$"), start)],
        )

        dp.add_handler(
            MessageHandler(Filters.regex('^❌ Не согласен$'), cancel_auth))
        dp.add_handler(conv_handler)
        dp.add_handler(CommandHandler("start", start))
        updater.start_polling()
        updater.idle()


def start(update, context):
    user = update.effective_user

    if not is_new_user(user.id):
        message_keyboard = [["✅ Личный кабинет", "❌ Получение рецептов"]]
        markup = ReplyKeyboardMarkup(message_keyboard, resize_keyboard=True)
        update.message.reply_text("С возвращением!", reply_markup=markup)
        return PERSONAL_ACCOUNT

    else:
        message_keyboard = [["✅ Согласен", "❌ Не согласен"]]
        markup = ReplyKeyboardMarkup(
            message_keyboard, resize_keyboard=True, one_time_keyboard=True
        )

        with open("files/Согласие.pdf", "rb") as image:
            user_agreement_pdf = image.read()

        update.message.reply_document(
            user_agreement_pdf,
            filename="Соглашение на обработку персональных данных.pdf",
            caption="Здравствуйте! Для продолжения использования бота, пожалуйста, подтвердите свое согласие на обработку персональных данных!",
            reply_markup=markup,
        )
        return USER_FULLNAME


def get_fullname(update, context):
    context.user_data["choice"] = "Имя и фамилия"
    update.message.reply_text(f"Введите имя и фамилию:")
    return PHONE_NUMBER


def get_phonenumber(update, context):
    user_data = context.user_data
    text = update.message.text
    user_choice = user_data['choice']
    user_data[user_choice] = text
    del user_data['choice']

    user_fullname = user_data['Имя и фамилия'].split()

    if not validate_fullname(user_fullname):
        update.message.reply_text(
            'Вы не указали фамилию или имя, попробуйте снова.')
        return get_fullname(update, context)

    context.user_data["choice"] = "Телефон"
    message_keyboard = [[KeyboardButton("Отправить свой номер телефона", request_contact=True)]]
    markup = ReplyKeyboardMarkup(message_keyboard, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text(f"Введите телефон в формате +7... или нажав на кнопку ниже:", reply_markup=markup)
    return END_AUTH


def end_auth(update, context):
    user_data = context.user_data

    if update.message.contact:
        text = update.message.contact.phone_number
    else:
        text = update.message.text

    check_number = validate_phonenumber(text)
    if check_number is False:
        update.message.reply_text(
            f"Вы неправильно ввели номер телефона"
        )
        return get_phonenumber(update, context)

    user_choice = user_data['choice']
    user_data[user_choice] = text

    if 'choice' in user_data:
        del user_data['choice']

        user_fullname = user_data['Имя и фамилия']
        user_phone_number = phonenumbers.parse(user_data['Телефон'], 'RU')
        user_id = update.effective_user.id

        user = {
            "user_id": user_id,
            "full_name": user_fullname,
            "phone_number": user_phone_number,
        }
        save_user_data(user)
        update.message.reply_text("Спасибо, вы зарегистрированы!❤️")

        return PERSONAL_ACCOUNT


def cancel_auth(update, context):
    message_keyboard = [["✅ Согласен", "❌ Не согласен"]]
    markup = ReplyKeyboardMarkup(
        message_keyboard, resize_keyboard=True, one_time_keyboard=True
    )
    update.message.reply_text(
        "Извините, тогда мы не сможем пропустить вас дальше.",
        reply_markup=markup,
    )
    return ConversationHandler.END


def personal_account(update, context):
    message_keyboard = [['Посмотреть заказы', 'Главное меню']]
    markup = ReplyKeyboardMarkup(message_keyboard, one_time_keyboard=True,
                                 resize_keyboard=True)
    update.message.reply_text('Выберите, что хотите сделать:', reply_markup=markup)
    return PERSONAL_ACCOUNT


def create_order(update, context):
    pass