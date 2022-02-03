import logging

from google.cloud import dialogflow

logger = logging.getLogger(__file__)


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
