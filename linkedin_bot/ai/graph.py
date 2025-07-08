from langchain_core.runnables.config import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph


from .agents.google_nodes import chatbot
from .configs import thread_config
from .states import PostsStoragingState


graph: StateGraph = (
    StateGraph(PostsStoragingState)
    .add_node(chatbot)
    .set_entry_point('chatbot')
    .set_finish_point('chatbot')
    .compile(checkpointer=MemorySaver())
)


async def start_graph(user_input: str, config: RunnableConfig = thread_config):
    response = await graph.ainvoke(input={'messages': user_input}, config=config)
    return response
