import logging
import os

from dotenv import load_dotenv
from google.cloud import dialogflow, storage
from telegram import Update, Bot
from telegram.ext import CallbackContext, CommandHandler, Filters
from telegram.ext import MessageHandler, Updater


load_dotenv()
logger = logging.getLogger(__file__)


class TelegramLogsHandler(logging.Handler):

    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def start(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text='Здравствуйте!'
    )


def echo(update: Update, context: CallbackContext):
    response = detect_intent_texts(
        project_id=project_id,
        session_id=update.effective_chat.id,
        text=update.message.text
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id, text=response
    )


def caps(update: Update, context: CallbackContext):
    text_caps = ' '.join(context.args).upper()
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text_caps
    )


def detect_intent_texts(project_id, session_id, text, language_code='ru'):
    session_client = dialogflow.SessionsClient()

    session = session_client.session_path(project_id, session_id)
    logger.debug(f'Session path: {session}\n')

    text_input = dialogflow.TextInput(
        text=text, language_code=language_code
    )

    query_input = dialogflow.QueryInput(text=text_input)
    response = session_client.detect_intent(
        request={'session': session, 'query_input': query_input}
    )

    logger.debug('=' * 20)
    logger.debug(f'Query text: {response.query_result.query_text}')
    logger.debug(
        f'Detected intent: {response.query_result.intent.display_name} '
        f'(confidence {response.query_result.intent_detection_confidence})'
    )
    logger.debug(
        f'Fullfillment text: {response.query_result.fulfillment_text}'
    )
    return response.query_result.fulfillment_text


def main():
    global project_id
    CBOT_BOT_TOKEN = os.environ['CBOT_BOT_TOKEN']
    CBOT_CHAT_ID = os.environ['CBOT_CHAT_ID']
    logging_bot = Bot(token=CBOT_BOT_TOKEN)
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG
    )
    logger.setLevel(logging.INFO)
    logger.addHandler(TelegramLogsHandler(logging_bot, CBOT_CHAT_ID))
    storage_client = storage.Client()
    tg_token = os.environ['TG_TOKEN']
    project_id = storage_client.project
    updater = Updater(
        token=tg_token,
        use_context=True
    )
    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    caps_handler = CommandHandler('caps', caps)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(echo_handler)
    dispatcher.add_handler(caps_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
