import json
from dotenv import load_dotenv
from google.cloud import dialogflow
from google.cloud import storage


load_dotenv()

storage_client = storage.Client()
project_id = storage_client.project


def create_intent(
    project_id, display_name, training_phrases_parts, message_texts
):
    print(project_id)
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

    print(f'Intent created: {response}')


def list_intents(project_id):
    intents_client = dialogflow.IntentsClient()
    parent = dialogflow.AgentsClient.agent_path(project_id)
    intents = intents_client.list_intents(request={'parent': parent})

    for intent in intents:
        print('=' * 20)
        print(
            f'Intent name: {intent.name}\nIntent display_name: '
            f'{intent.display_name}\nAction: {intent.action}\nRoot followup '
            f'intent: {intent.root_followup_intent_name}\n'
            f'Parent followup intent: {intent.parent_followup_intent_name}\n'
            f'Input contexts:'
        )
        for input_context_name in intent.input_context_names:
            print(f'\tName: {input_context_name}\n')

        print('Output contexts:\n')
        for output_context in intent.output_contexts:
            print(f'\tName: {output_context.name}')


def parse_file(filename):
    with open(filename, mode='r', encoding='utf-8') as f:
        file_content = json.load(f)
    for name in file_content:
        questions = file_content[name]['questions']
        answer = file_content[name]['answer']
        create_intent(project_id, name, questions, answer)


if __name__ == '__main__':
    parse_file('questions.json')
