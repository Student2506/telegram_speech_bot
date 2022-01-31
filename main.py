import logging
import os

from dotenv import load_dotenv
from google.cloud import dialogflow, storage
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, Filters
from telegram.ext import MessageHandler, Updater


load_dotenv()


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
    logging.debug(f'Session path: {session}\n')

    text_input = dialogflow.TextInput(
        text=text, language_code=language_code
    )

    query_input = dialogflow.QueryInput(text=text_input)
    response = session_client.detect_intent(
        request={'session': session, 'query_input': query_input}
    )

    logging.debug('=' * 20)
    logging.debug(f'Query text: {response.query_result.query_text}')
    logging.debug(
        f'Detected intent: {response.query_result.intent.display_name} '
        f'(confidence {response.query_result.intent_detection_confidence})'
    )
    logging.debug(
        f'Fullfillment text: {response.query_result.fulfillment_text}'
    )
    return response.query_result.fulfillment_text


if __name__ == '__main__':
    storage_client = storage.Client()
    tg_token = os.environ['TG_TOKEN']
    project_id = storage_client.project
    updater = Updater(
        token=tg_token,
        use_context=True
    )
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG
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
