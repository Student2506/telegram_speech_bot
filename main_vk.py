import os

import vk_api
from dotenv import load_dotenv
from vk_api.longpoll import VkLongPoll, VkEventType


load_dotenv()

vk_session = vk_api.VkApi(token=os.getenv('VK_TOKEN'))
longpoll = VkLongPoll(vk_session)

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        print('Новое сообщение:')
        if event.to_me:
            print(f'Для меня от: {event.user_id}')
        else:
            print(f'От меня для: {event.user_id}')
        print(f'Текст: {event.text}')
