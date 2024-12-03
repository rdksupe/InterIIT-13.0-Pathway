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
from Agents.LATS.utils import llm_to_check
load_dotenv('../../../.env')

prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                Your task is to generate a very detailed response backed by numbers and sources to the user question below
                1. First everytime use query_document to get the detailed response,if the response is not satisfactory or the tool fails ,then next step
                2.Then use specialized tools to generate the response,if the tools fail to generate a satisfactory response, then use web search to get the detailed response.
                3. For anything related to legal, use Indian Kanoon or US Case Law API to get the detailed response, if the API fails to generate a satisfactory response, then use web search to get the detailed response, this can be followed by using web scraper tools to get the detailed response,from the relevant webpages.
                Cite the sources,the link of the exact webpage  next to there relevant information in each response,used to get that information
                4. A detailed section dedicated to all the tools called earlier, and the count the number of times for the tools that failed to generate a satisfactory response.
                4. Clearly state any tool that failed ,if fails more than 2 times do not use that tool again in the response.
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
        

        llm_to_check = ChatOpenAI(model="gpt-4o-mini",openai_api_key=os.getenv("OPEN_AI_API_KEY_30_TEST"))


        initial_answer_chain = prompt_template | llm_to_check.bind_tools(tools=tools).with_config(
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