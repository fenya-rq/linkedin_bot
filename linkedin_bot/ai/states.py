from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, AnyMessage
from langgraph.graph import add_messages
from pydantic import BaseModel, Field


class BaseState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


class PostsStoragingState(BaseState):
    target_posts: Annotated[list[AIMessage], add_messages]
