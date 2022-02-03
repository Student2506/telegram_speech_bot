import logging
import os
import random
from contextlib import suppress

import telegram
import vk_api as vk
from dotenv import load_dotenv
from google.cloud import storage
from vk_api.longpoll import VkEventType, VkLongPoll

from google_dialogflow_api.py import detect_intent_texts
from logging_to_telegram import TelegramLogsHandler

logger = logging.getLogger(__file__)


def process_request(event, vk_api, project_id):
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


def main():
    load_dotenv()
    cbot_bot_token = os.environ['CBOT_BOT_TOKEN']
    cbot_chat_id = os.environ['CBOT_CHAT_ID']
    logging_bot = telegram.Bot(token=cbot_bot_token)
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG
    )
    logger.setLevel(logging.INFO)
    logger.addHandler(TelegramLogsHandler(logging_bot, cbot_chat_id))
    storage_client = storage.Client()
    project_id = storage_client.project
    vk_session = vk.VkApi(token=os.getenv('VK_TOKEN'))
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    with suppress(KeyboardInterrupt):
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                process_request(event, vk_api, project_id)


if __name__ == '__main__':
    main()
