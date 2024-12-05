from langchain_core.output_parsers.openai_tools import (
    JsonOutputToolsParser,
    PydanticToolsParser,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from Agents.LATS.TreeState import TreeState
from Agents.LATS.Reflection import reflection_chain, Node
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langgraph.prebuilt import ToolNode
from Agents.LATS.NewTools import *
import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv('../../../.env')

from LLMs import GPT4o_mini_LATS

prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                Generate a detailed response backed by numbers and sources to the user question below
                1. Use specialized tools to generate the response,if the tools fail to generate a satisfactory response, then use web search to get the detailed response.
                2. Cite the sources,the link of the exact webpage  next to there relevant information in each response,used to get that information
                3. If a tool says it has failed, switch to the next tool. DO NOT USE THE SAME TOOL AGAIN
                """,
            ),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="messages", optional=True),
        ]
    )

# Define the node we will add to the graph
def custom_generate_initial_response(tools):
    tool_node = ToolNode(tools=tools)
    def generate_initial_response(state: TreeState) -> dict:
        initial_answer_chain = prompt_template | GPT4o_mini_LATS.bind_tools(tools=tools).with_config(
            run_name="GenerateInitialCandidate"
        )

        parser = JsonOutputToolsParser(return_id=True)

        """Generate the initial candidate response."""
        res = initial_answer_chain.invoke({"input": state["input"]})
        parsed = parser.invoke(res)
        tool_responses = [
            tool_node.invoke(
                {
                    "messages": [
                        AIMessage(
                            content="",
                            tool_calls=[
                                {"name": r["type"], "args": r["args"], "id": r["id"]}
                            ],
                        )
                    ]
                }

            )
            for r in parsed
        ]
        output_messages = [res] + [tr["messages"][0] for tr in tool_responses]
        reflection = reflection_chain.invoke(
            {"input": state["input"], "candidate": output_messages}
        )
        root = Node(output_messages, reflection=reflection)
        return {
            **state,
            "root": root,
        }
    return generate_initial_response