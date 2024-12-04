import os
from dotenv import load_dotenv
load_dotenv('../.env')

import time
import json
import google.generativeai as genai
import re

from Agents.Agents import Agent
from Agents.Smack import Smack
from Agents.ClassifierAgent import classifierAgent
from Agents.PlannerAgent import plannerAgent
from Agents.ChartGenAgent import generate_chart
from Agents.DrafterAgent import drafterAgent_vanilla, drafterAgent_rag
from Agents.ConciseAnsAgent import conciseAns_vanilla, conciseAns_rag
from Agents.RAG_Agent import ragAgent
from Agents.LATS.Solve_subquery import SolveSubQuery
from Agents.conciseLatsAgent import conciseAns_vanilla_LATS
from langchain_community.callbacks import get_openai_callback
from langchain_openai import ChatOpenAI

from Agents.LATS.NewTools import *
import json
import threading
import asyncio
import websockets

from langchain.globals import set_verbose

import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Any
from collections import defaultdict

from makeGraphJSON import makeGraphJSON
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from TopicalGuardrails import applyTopicalGuardails
from GenerateQuestions import genQuestionComplex, genQuestionSimple
class  MyHandler(FileSystemEventHandler):
    def __init__(self, websocket_connection) -> None:
        super().__init__()
        self.websocket = websocket_connection  # WebSocket connection passed here

    async def on_modified(self, event):
        # Printing the event type and path
        print(f'Event type: {event.event_type} path: {event.src_path}')
        
        # Sending the event details over the WebSocket connection asynchronously
        message = {
            "type": "agents",
            "response": f'Event type: {event.event_type} path: {event.src_path}'
        }
        
        if self.websocket.open:
            await self.websocket.send(json.dumps(message))

    def  on_created(self,  event):
         print(f'event type: {event.event_type} path : {event.src_path}')
    def  on_deleted(self,  event):
         print(f'event type: {event.event_type} path : {event.src_path}')

set_verbose(True)
now = time.time()

query = '''
Evaluate the financial performance of BTG's key product lines in the last two years, highlighting any segments experiencing significant revenue decline or margin
'''
async def mainBackend(query, websocket):
    print("Running mainBackend, ", query)
    GOOGLE_API_KEY = os.getenv('GEMINI_API_KEY_30')
    OPENAI_API_KEY = os.getenv('OPEN_AI_API_KEY_30')
    os.makedirs('./output', exist_ok=True)
    LLM = 'OPENAI'
    key_dict = {
        'OPENAI': OPENAI_API_KEY,
        'GEMINI': GOOGLE_API_KEY
    }
    api_key = key_dict[LLM]


    IS_RAG = False

    with open("ProcessLogs.md", "w") as f:
        f.write("")
    with open("tickers.txt", "a") as f_ticker:
        f_ticker.write('')

    guard_rails, reasonings = applyTopicalGuardails(query)
    if guard_rails:
        query_type = classifierAgent(query, GOOGLE_API_KEY).lower()
        if query_type == "complex":
            print("RUNNING COMPLEX TASK PIPELINE")
            plan = plannerAgent(query, api_key, LLM)

            #This is the dictionary for UI Graph Construction
            dic_for_UI_graph = makeGraphJSON(plan['sub_tasks'])
            print(dic_for_UI_graph)
            await asyncio.sleep(1)
            await websocket.send(json.dumps({"type": "graph", "response": json.dumps(dic_for_UI_graph)}))

            with open('Graph.json', 'w') as fp:
                json.dump(dic_for_UI_graph, fp)
            
            out_str = ''''''

            agentsList = []
            addn_questions = []
            
            for sub_task in plan['sub_tasks']:
                addn_questions.append(plan['sub_tasks'][sub_task]['content'])
                agent_name = plan['sub_tasks'][sub_task]['agent']
                agent_role = plan['sub_tasks'][sub_task]['agent_role_description']
                local_constraints = plan['sub_tasks'][sub_task]['local_constraints']
                task = plan['sub_tasks'][sub_task]['content']
                dependencies = plan['sub_tasks'][sub_task]['require_data']
                tools_list = plan['sub_tasks'][sub_task]['tools']
                print(f'processing {agent_name}')
                agent = Agent(sub_task, agent_name, agent_role, local_constraints, task,dependencies, api_key, tools_list, LLM)
                agentsList.append(agent)
            
            
            smack = Smack(agentsList)
            taskResultsDict = smack.executeSmack()
            for task in taskResultsDict:
                out_str += f'{taskResultsDict[task]} \n'
            resp = ''
            #Need to test this later
            if IS_RAG == True:
                rag_context, rag_processed_response = ragAgent(query, key_dict[LLM], LLM, state = 'report')
                out_str = f'{rag_processed_response}\n \n{out_str}'
                resp = drafterAgent_rag(query, rag_context, out_str, api_key, LLM)
                resp = str(resp)
                await asyncio.sleep(1)
                await websocket.send(json.dumps({"type": "response", "response": resp}))
            #Tested multiple times
            else:
                resp = drafterAgent_vanilla(query, out_str, api_key, LLM)
                
            with open ('./output/drafted_response.md', 'w') as f:
                if LLM=='GEMINI':
                    resp = re.sub(r'\\\[(.*?)\\\]', lambda m: f'$${m.group(1)}$$', resp, flags=re.DOTALL)
                    resp = generate_chart(resp)
                    f.write(str(resp))
                elif LLM=='OPENAI':
                    resp = re.sub(r'\\\[(.*?)\\\]', lambda m: f'$${m.group(1)}$$', resp, flags=re.DOTALL)
                    resp = generate_chart(resp)
                    f.write(str(resp))

            final_questions = []
            for question in addn_questions:
                refinedQuestion = genQuestionComplex(query, question)
                final_questions.append(question)

            await asyncio.sleep(1)
            await websocket.send(json.dumps({"type": "response", "response": resp}))
            await websocket.send(json.dumps({"type": "questions", "response": '\n'.join(final_questions)}))
            
        elif query_type == 'simple':
            print("RUNNING SIMPLE TASK PIPELINE")
            
            async def executeSimplePipeline(query):
                resp = ''
                if IS_RAG == True:
                    rag_context = ragAgent(query, key_dict[LLM], LLM, state = "concise")
                    resp = conciseAns_rag(query, rag_context, out_str, api_key, LLM)['output']

                else:
                    tools_list = [get_stock_data, web_search_simple, get_company_profile, get_basic_financials, get_company_info, get_stock_dividends, get_income_stmt, get_balance_sheet, get_cash_flow, get_analyst_recommendations]
                    resp = conciseAns_vanilla(query, tools_list)
                    resp = resp['output']
                return str(resp)

            async def run_parallel(query):
                resp, additionalQuestions = await asyncio.gather(
                    executeSimplePipeline(query),
                    genQuestionSimple(query)
                )
                
                return (str(resp), str(additionalQuestions))
            resp, additionalQuestions = await run_parallel(query)
            #additionalQuestions = '\n'.join(additionalQuestions.values())

            await asyncio.sleep(1)
            await websocket.send(json.dumps({"type": "response", "response": resp}))
            await websocket.send(json.dumps({"type": "questions", "response": additionalQuestions}))
    else:
        resp = ''''''
        for key in reasonings:
            resp += f'''**{key}**\n\n'''
            resp += f'''{reasonings[key]}\n\n'''
        with open("Bad_Question.md", "w") as f:
            f.write(resp)
        print(f'Total Time: {time.time()-now}')
        await asyncio.sleep(1)
        await websocket.send(json.dumps({"type": "response", "response": resp}))

async def handle_connection(websocket):
    #try:
        # observer_thread = threading.Thread(target=start_observer,args=(websocket), daemon=True)
        # observer_thread.start()
    async for message in websocket:
        data = json.loads(message)
        if data['type'] == 'query':
            print(f"Received query: {data['query']}")
            await mainBackend(data['query'], websocket)
            # resp = str(fin_resp)
            # await asyncio.sleep(1)
            # await websocket.send(json.dumps({"type": "response", "response": resp}))
        if data['type'] == 'cred':
                print(f"Received credentials: {data['formData']}")
                        # Read the current .env file
                env_file_path = '../.env'
                with open(env_file_path, 'r') as fp:
                    env_content = fp.readlines()

                # Create a dictionary to hold the current environment variables
                env_dict = {}
                for line in env_content:
                    # Ignore comments and empty lines
                    if line.strip() and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        value = value.strip('"')
                        env_dict[key] = value

                # Update the env_dict with new values from formData
                form_data = data['formData']
                for key, value in form_data.items():
                    if value:  # Only update if the value is not empty
                        if key in env_dict:
                            print(f"Updating API key for {key}")
                        else:
                            print(f"Adding new API key for {key}")
                        env_dict[key] = value

                # Write the updated environment variables back to the .env file
                with open(env_file_path, 'w') as fp:
                    for key, value in env_dict.items():
                        fp.write(f"{key}=\"{value}\"\n")

                print(".env file has been updated.")
    #except websockets.exceptions.ConnectionClosed:
    #    print("Client connection closed")
    #except Exception as e:
    #    print(f"Error handling connection: {e}")

async def main():
    print("WebSocket server starting on ws://0.0.0.0:8080")
    async with websockets.serve(handle_connection, "localhost", 8080):
        await asyncio.Future()  # run forever

def start_observer(websocket):
    event_handler = MyHandler(websocket)
    observer = Observer()
    observer.schedule(event_handler,  path='C:\\temp\\flask\\final\\tech-meet-13\\RACCOON\\LOG',  recursive=False)
    observer.start()

    try:
        while  True:
            time.sleep(1)
            print("Running")
    except  KeyboardInterrupt:
        observer.stop()
    observer.join()

def run_observer_in_thread():
    observer_thread = threading.Thread(target=start_observer, daemon=True)
    observer_thread.start()
    return observer_thread

async def start():
    # Run WebSocket server
    websocket_task = asyncio.create_task(main())

    # Run the observer in a separate thread
    observer_thread = run_observer_in_thread()

    # Wait for the WebSocket server to finish (this will run forever)
    await websocket_task

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer shutdown by user")