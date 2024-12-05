import os
import json
from dotenv import load_dotenv
import time
load_dotenv('../../.env')

from datetime import datetime
import google.generativeai as genai

from langchain.globals import set_verbose
set_verbose(True)

from Agents.LATS.NewTools import *

from LLMs import conversation_complex



def clean(text):
    return text[text.index('{'):text.rfind('}')+1]


def ragAgent(query, state):
    fin_context = ''''''
    
    if state == "report":
        rag_result = retrieve_documents.invoke(query)
        fin_context += f'{rag_result} \n'
        sys_prompt =  '''
        Extract the Key Words, Jargons and Important Concepts from the information given below and make queries in order to query a 
        document retriever to extract more context about the extract and query. Make at most 3 queries which encompass all the 
        concepts and jargons. Strictly format is like a dictionary with schema:
        {
            "query_1": "...",
            "query_2": "...",
            "query_3": "..."
        }
        Following is the information to be used:
        \n
        '''

        prompt = f"""Note: The Current Date and Time is {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}. All your searches and responses must be with respect to this time frame""" + sys_prompt + rag_result
        '''client = OpenAI(api_key = os.getenv('OPEN_AI_API_KEY_30'))
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        response = completion.choices[0].message.content.strip()
        '''
        response = conversation_complex.predict(input = f'''{prompt}''')
        
        dic =  dict(json.loads(clean(response.split("```")[-2].split("json")[1])))
        for p in dic:
            rag_resp = retrieve_documents.invoke(query)
            fin_context += f'{rag_resp} \n'

        prompt_2 =  f'''
        Note: The Current Date and Time is {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}. All your searches and responses
        must be with respect to this time frame
        
        Based on the given main query, 3 sub-queries, and given context, conduct intensive research from 
        a multi-domain perspective (such as finance, economics, law, market research, consumer research, compliance etc)
        and generate a comprehensive answer to the main query.
        The main query is: {query}
        The sub-queries are: {dic}
        The context is: {fin_context}
        The answer should be backed by all the facts gathered and research conducted, hence the answer should be extremely detailed.
        \n
        '''
        '''completion_2 = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": prompt_2
                }
            ]
        )
        fin_response = completion_2.choices[0].message.content.strip()'''

        fin_response = conversation_complex.predict(input = f'''{prompt_2}''')

        return fin_context, fin_response
        
    elif state == "concise":
        print("Hello This is concise")
        return simple_query_documents.invoke(query)