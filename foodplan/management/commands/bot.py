import os

from dotenv import load_dotenv
from django.core.management.base import BaseCommand

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


class Command(BaseCommand):
    help = 'Телеграм бот'

    def handle(self, *args, **options):
        load_dotenv()
        updater = Updater(os.getenv("TELEGRAM_TOKEN"), use_context=True)
        dp = updater.dispatcher
        dp.add_handler(MessageHandler(Filters.text, hello))
        updater.start_polling()


def hello(update, context):
    update.message.reply_text(
        f"hello {update.effective_user.first_name}"
    )


