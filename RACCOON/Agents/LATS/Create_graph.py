from typing import Literal
from Agents.LATS.Initial_response import custom_generate_initial_response
from Agents.LATS.TreeState import TreeState
from Agents.LATS.generate_candiates import custom_expand
from langgraph.graph import END, StateGraph, START
from Agents.LATS.NewTools import *
from dotenv import load_dotenv
load_dotenv()

def should_loop(state: TreeState):
    """Determine whether to continue the tree search."""
    root = state["root"]
    if root.is_solved:
        return END
    if root.height > 3:
        return END
    return "expand"

def generateGraph_forLATS(tools):
    builder = StateGraph(TreeState)
    builder.add_node("start", custom_generate_initial_response(tools))
    builder.add_node("expand", custom_expand(tools))
    builder.add_edge(START, "start")

    builder.add_conditional_edges(
        "start",
        # Either expand/rollout or finish
        should_loop,
        ["expand", END],
    )
    builder.add_conditional_edges(
        "expand",
        # Either continue to rollout or finish
        should_loop,
        ["expand", END],
    )

    graph = builder.compile()

    return graph