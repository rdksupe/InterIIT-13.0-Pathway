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

from langchain.globals import set_verbose

import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Any
from collections import defaultdict

from makeGraphJSON import makeGraphJSON

from TopicalGuardrails import applyTopicalGuardails

set_verbose(True)
now = time.time()

GOOGLE_API_KEY = os.getenv('GEMINI_API_KEY_30')
OPENAI_API_KEY = os.getenv('OPEN_AI_API_KEY_30')


LLM = 'OPENAI'

key_dict = {
    'OPENAI': OPENAI_API_KEY,
    'GEMINI': GOOGLE_API_KEY
}

IS_RAG = False

with open("ProcessLogs.md", "w") as f:
    f.write("")
with open("tickers.txt", "a") as f_ticker:
    f_ticker.write('')

query = '''
How the fuck did the motherfucking company Microsoft become so fucking big.
'''

if applyTopicalGuardails(query):
    query_type = classifierAgent(query, GOOGLE_API_KEY).lower()
    if query_type == "complex":
        print("RUNNING COMPLEX TASK PIPELINE")
        api_key = key_dict[LLM]
        plan = plannerAgent(query, api_key, LLM)

        #This is the dictionary for UI Graph Construction
        dic_for_UI_graph = makeGraphJSON(plan['sub_tasks'])
        with open('Graph.json', 'w') as fp:
            json.dump(dic_for_UI_graph, fp)
        pass
        
        response_dict = dict()
        out_str = ''''''

        agentsList = []
        
        for sub_task in plan['sub_tasks']:
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

        #Need to test this later
        if IS_RAG == True:
            rag_context, rag_processed_response = ragAgent(query, key_dict[LLM], LLM, state = 'report')
            out_str = f'{rag_processed_response}\n \n{out_str}'
            fin_resp = drafterAgent_rag(query, rag_context, out_str, api_key, LLM)
        #Tested multiple times
        else:
            fin_resp = drafterAgent_vanilla(query, out_str, api_key, LLM)
        os.makedirs('./output', exist_ok=True)
        with open('./output/individual_response.json', 'w') as json_file:
            json.dump(taskResultsDict, json_file, indent=4)

        with open ('./output/raw_response.md', 'w') as f:
            if LLM=='GEMINI':
                f.write(str(out_str))
            elif LLM=='OPENAI':
                f.write(str(out_str))
        with open ('./output/drafted_response.md', 'w') as f:
            if LLM=='GEMINI':
                fin_resp = re.sub(r'\\\[(.*?)\\\]', lambda m: f'$${m.group(1)}$$', fin_resp, flags=re.DOTALL)
                f.write(str(fin_resp))
            elif LLM=='OPENAI':
                fin_resp = re.sub(r'\\\[(.*?)\\\]', lambda m: f'$${m.group(1)}$$', fin_resp, flags=re.DOTALL)
                f.write(str(fin_resp))
        with open ('./output/response_1.md', 'w') as f:
            print(type(taskResultsDict[sub_task]))
            print(taskResultsDict[sub_task])
            f.write(taskResultsDict[sub_task])

        generate_chart("output/drafted_response.md")
        
    elif query_type == 'simple':
        tools_list = [get_stock_data, web_search_simple, get_company_profile, get_basic_financials, get_company_info, get_stock_dividends, get_income_stmt, get_balance_sheet, get_cash_flow, get_analyst_recommendations]
        
        #Need to test this later
        if IS_RAG == True:
            rag_context = ragAgent(query, key_dict[LLM], LLM, state = "concise")
            fin_resp = conciseAns_rag(query, rag_context, out_str, api_key, LLM)['output']

        else:
            def run_parallel():
                with ThreadPoolExecutor() as executor:
                    # Define the tasks
                    future_resp_lats = executor.submit(conciseAns_vanilla_LATS, query, tools_list)
                    future_resp = executor.submit(conciseAns_vanilla, query, key_dict[LLM], LLM, tools_list)
                    # Get the results
                    fin_resp = future_resp.result()['output']
                    fin_resp_lats = future_resp_lats.result()
                return fin_resp, fin_resp_lats
            
            fin_resp, fin_resp_lats = run_parallel()
else:
    print("Sudhar ja Bhosdike")

print(f'Total Time: {time.time()-now}')