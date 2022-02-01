import logging
import os
import random

import telegram
import vk_api as vk
from dotenv import load_dotenv
from google.cloud import dialogflow, storage
from vk_api.longpoll import VkEventType, VkLongPoll

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


def echo(event, vk_api):
    response = detect_intent_texts(
        project_id=project_id,
        session_id=event.user_id,
        text=event.text
    )
    if response:
        vk_api.messages.send(
            user_id=event.user_id,
            message=response,
            random_id=random.randint(1, 1000)
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
    if response.query_result.intent.is_fallback:
        return None
    return response.query_result.fulfillment_text


def main():
    global project_id
    CBOT_BOT_TOKEN = os.environ['CBOT_BOT_TOKEN']
    CBOT_CHAT_ID = os.environ['CBOT_CHAT_ID']
    logging_bot = telegram.Bot(token=CBOT_BOT_TOKEN)
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG
    )
    logger.setLevel(logging.INFO)
    logger.addHandler(TelegramLogsHandler(logging_bot, CBOT_CHAT_ID))
    storage_client = storage.Client()
    project_id = storage_client.project
    vk_session = vk.VkApi(token=os.getenv('VK_TOKEN'))
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    try:
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                echo(event, vk_api)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
