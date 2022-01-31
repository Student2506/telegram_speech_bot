import logging
import os
import random

import vk_api as vk
from dotenv import load_dotenv
from google.cloud import dialogflow, storage
from vk_api.longpoll import VkEventType, VkLongPoll

load_dotenv()
storage_client = storage.Client()
project_id = storage_client.project


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def echo(event, vk_api):
    response = detect_intent_texts(
        project_id=project_id,
        session_id=event.user_id,
        text=event.text
    )
    vk_api.messages.send(
        user_id=event.user_id,
        message=response,
        random_id=random.randint(1, 1000)
    )


def detect_intent_texts(project_id, session_id, text, language_code='ru'):
    session_client = dialogflow.SessionsClient()

    session = session_client.session_path(project_id, session_id)
    print(f'Session path: {session}\n')

    text_input = dialogflow.TextInput(
        text=text, language_code=language_code
    )

    query_input = dialogflow.QueryInput(text=text_input)
    response = session_client.detect_intent(
        request={'session': session, 'query_input': query_input}
    )

    print('=' * 20)
    print(f'Query text: {response.query_result.query_text}')
    print(
        f'Detected intent: {response.query_result.intent.display_name} '
        f'(confidence {response.query_result.intent_detection_confidence})'
    )
    print(f'Fullfillment text: {response.query_result.fulfillment_text}')
    return response.query_result.fulfillment_text


if __name__ == '__main__':
    vk_session = vk.VkApi(token=os.getenv('VK_TOKEN'))
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    try:
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                echo(event, vk_api)
    except KeyboardInterrupt:
        pass
