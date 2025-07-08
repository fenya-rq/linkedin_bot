from typing import Annotated, TypedDict

from langchain.chat_models import init_chat_model
from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages

from .llm_rules import linkedin_instructions


gemini_agent = init_chat_model(
    'google_genai:gemma-3n-e4b-it',
    max_output_tokens=500,
    google_api_key=GEMINI_API_KEY,
    top_k=40,
    top_p=0.9,
    temperature=0.3,
    model_kwargs={
        'system_instruction': linkedin_instructions
    }
)


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


async def chatbot(state: State):
    print(state['messages'])
    response = await gemini_agent.ainvoke(state['messages'])
    return response
