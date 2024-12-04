import google.generativeai as genai
import os
from datetime import datetime
from dotenv import load_dotenv
import json

from LLMs import conversation_complex

load_dotenv('../.env')

OPENAI_API_KEY = os.getenv('OPEN_AI_API_KEY_30')

def genQuestionComplex(main_query, sub_task):
    system_prompt = f'''
    Rephrase the following User Prompt without dependance on all task_n or any document. Ensure that there is no phrase like "based on...":

    The context  to this has to be:

    {main_query}

    '''

    user_prompt = f'''
    The User Prompt is

    {sub_task}
    '''

    prompt = f'''{system_prompt}\n\n {user_prompt}'''
    
    '''client = OpenAI(api_key=api_key)
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    )
    response = completion.choices[0].message.content.strip()'''

    response = conversation_complex.run(f'''{prompt}''')

    return response

def genQuestionSimple(query):
    print("Executing genQuestionSimple")
    system_prompt = '''
        Synthesize 5 Questions Related to the given query. 
        Instructions to make the questions:
        - The questions should be such that their answers can be detailed reports, this means that the answering those questions would require in depth research and reasoning
        - The questions should be related to the following domains: finance, economics, law, markets, technology, politics, environment, consumers etc. Questions can also be multidisciplinary, combining facts from multiple domains.
        - Try to make the questions as diverse as possible, but you must not deviate from the original query given. 
        - The questions should be *at least* 20 words long
        - Output the questions according to the schema:
        {
        "question1": "...",
        "question2": "...",
        "question3": "...",
        "question4": "...",
        "question5": "..."
        }
    '''

    user_prompt = f'''
    The User Prompt is

    {query}
    '''

    prompt = f'''{system_prompt}\n\n {user_prompt}'''
    response = conversation_complex.run(f'''{prompt}''')
    
    '''client = OpenAI(api_key=api_key)
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    )
    response = completion.choices[0].message.content.strip()'''
    print("Executed genQuestionSimple")
    return json.loads(response)