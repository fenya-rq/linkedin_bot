import json

from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, HumanMessage

from linkedin_bot.ai.states import PostsStoragingState
from linkedin_bot.config import GEMINI_API_KEY, main_logger
from linkedin_bot.utilities.custom_exceptions import JSONNotFound
from linkedin_bot.utilities.utils import clean_json, log_writer
from .llm_rules import prompt_rules

gemini_agent = init_chat_model(
    'google_genai:gemma-3n-e4b-it',
    max_output_tokens=500,
    google_api_key=GEMINI_API_KEY,
    top_k=40,
    top_p=0.9,
    temperature=0.2
)


async def chatbot(state: PostsStoragingState):
    last_msg = state['messages'][-1]

    prompt_with_rules = f'{prompt_rules}\n{last_msg.content}'

    analysis = await gemini_agent.ainvoke([HumanMessage(content=prompt_with_rules)])

    try:
        analysis_result = clean_json(analysis.content, load=True)
    except (JSONNotFound, Exception) as e:
        log_writer(main_logger, 40,f'Analysis parsing error: {e}')
        return {'target_posts': state['target_posts']}

    if analysis_result.get('allowed'):
        post_data = analysis_result.get('post', {})
        str_content = '\n'.join(f'{k}: {v}' for k, v in post_data.items())
        state['target_posts'].append(AIMessage(content=str_content))

    return {'target_posts': state['target_posts']}
