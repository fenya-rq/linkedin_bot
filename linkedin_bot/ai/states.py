from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages

class BaseState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

class PostsStoragingState(BaseState):
    target_posts: Annotated[list[AnyMessage], add_messages]
