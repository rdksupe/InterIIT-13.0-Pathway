import google.generativeai as genai
import os
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv('../.env')

OPENAI_API_KEY = os.getenv('OPEN_AI_API_KEY_30')

def genQuestion(main_query, sub_task, api_key, LLM):
    system_prompt = f'''
    Rephrase the following User Prompt without dependance on all task_n or any document. Ensure that there is no phrase like "based on...":

    The context  to this has to be:

    {main_query}

    '''

    user_prompt = f'''
    The User Prompt is

    {sub_task}
    '''
    
    client = OpenAI(api_key=api_key)
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
    response = completion.choices[0].message.content.strip()

    return response