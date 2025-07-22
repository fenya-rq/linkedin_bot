import time

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage

from linkedin_bot.ai.utils import GlobalSharedState
from linkedin_bot.config import GEMINI_API_KEY, main_logger
from linkedin_bot.utilities.async_utils.limiters import TokenLimiter
from linkedin_bot.utilities.custom_exceptions import JSONNotFoundError
from linkedin_bot.utilities.utils import clean_json, log_writer

from .llm_rules import prompt_rules

gemini_agent = init_chat_model(
    'google_genai:gemma-3n-e4b-it',
    max_output_tokens=500,
    google_api_key=GEMINI_API_KEY,
    top_k=40,
    top_p=0.9,
    temperature=0.2,
)


async def analyze_posts(
    user_input: str, shared_state: GlobalSharedState, token_limiter: TokenLimiter, max_attempts=3
):
    attempt = 1

    while attempt <= max_attempts:
        prompt_with_rules = f'{prompt_rules}\n{user_input}'

        await token_limiter.spend_tokens(1200)

        analysis = await gemini_agent.ainvoke([HumanMessage(content=prompt_with_rules)])

        try:
            analysis_result = clean_json(analysis.content, load=True)

            if analysis_result.get('allowed'):
                post_data = analysis_result.get('post', {})
                str_content = '\n'.join(f'{k}: {v}' for k, v in post_data.items())
                shared_state['target_posts'].append(f'{str_content}\n')
                log_writer(main_logger, 40, f' === {str_content}')

        except (JSONNotFoundError, Exception) as e:
            log_writer(main_logger, 40, f'Analysis parsing error: {e}')
            return

        except Exception as e:
            if attempt == max_attempts:
                print(
                    f'[analyze_posts_with_retry] All {max_attempts} attempts failed.'
                    f' Last error: {e}'
                )
                raise  # re-raise last exception
            else:
                print(
                    f'[analyze_posts_with_retry] Attempt {attempt} failed: {e}. Retrying in 60s...'
                )
                time.sleep(
                    60
                )  # TEMPORARY FOR DEV! Blocking sleep to real freeze code for 1 minute.
                attempt += 1
