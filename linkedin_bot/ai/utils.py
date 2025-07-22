from typing import TypedDict


class GlobalSharedState(TypedDict):
    spent_tokens: int
    target_posts: list
