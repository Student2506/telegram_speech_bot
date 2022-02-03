import logging
import os
from functools import partial

from dotenv import load_dotenv
from google.cloud import storage
from telegram import Bot, Update
from telegram.ext import CallbackContext, CommandHandler, Filters
from telegram.ext import MessageHandler, Updater

from google_dialogflow_api import detect_intent_texts
from logging_to_telegram import TelegramLogsHandler

logger = logging.getLogger(__file__)


def start(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text='Здравствуйте!'
    )


def process_request(update: Update, context: CallbackContext, project_id):
    response = detect_intent_texts(
        project_id=project_id,
        session_id=update.effective_chat.id,
        text=update.message.text
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id, text=response
    )


def main():
    load_dotenv()
    cbot_bot_token = os.environ['CBOT_BOT_TOKEN']
    cbot_chat_id = os.environ['CBOT_CHAT_ID']
    logging_bot = Bot(token=cbot_bot_token)
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG
    )
    logger.setLevel(logging.INFO)
    logger.addHandler(TelegramLogsHandler(logging_bot, cbot_chat_id))
    storage_client = storage.Client()
    tg_token = os.environ['TG_TOKEN']
    project_id = storage_client.project
    updater = Updater(
        token=tg_token,
        use_context=True
    )
    start_handler = CommandHandler('start', start)
    request_handler = MessageHandler(
        Filters.text & (~Filters.command),
        partial(process_request, project_id=project_id)
    )
    dispatcher = updater.dispatcher
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(request_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
