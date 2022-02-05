import json
import logging

import configargparse
from dotenv import load_dotenv
from google.cloud import dialogflow, storage

FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

log = logging.getLogger(__name__)


def create_intent(
    project_id, display_name, training_phrases_parts, message_texts
):
    log.debug(f'{project_id}')
    intents_client = dialogflow.IntentsClient()
    parent = dialogflow.AgentsClient.agent_path(project_id)
    training_phrases = []
    for training_phrases_part in training_phrases_parts:
        part = dialogflow.Intent.TrainingPhrase.Part(
            text=training_phrases_part
        )
        training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
        training_phrases.append(training_phrase)

    text = dialogflow.Intent.Message.Text(text=[message_texts])
    message = dialogflow.Intent.Message(text=text)
    intent = dialogflow.Intent(
        display_name=display_name,
        training_phrases=training_phrases,
        messages=[message]
    )

    response = intents_client.create_intent(
        request={'parent': parent, 'intent': intent}
    )

    log.debug(f'Intent created: {response}')


def main():
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    configs = configargparse.ArgParser()
    configs.add(
        '-i', '--filename', default='questions.json', help='file to import'
    )
    filename = configs.parse_args().filename
    load_dotenv()
    storage_client = storage.Client()
    project_id = storage_client.project
    with open(filename, mode='r', encoding='utf-8') as f:
        file_content = json.load(f)
    for name in file_content:
        questions = file_content[name]['questions']
        answer = file_content[name]['answer']
        create_intent(project_id, name, questions, answer)


if __name__ == '__main__':
    main()
