import google.generativeai as genai
import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv('../../.env')

OPENAI_API_KEY = os.getenv('OPEN_AI_API_KEY_30')
print(OPENAI_API_KEY)
client = OpenAI(
    api_key=OPENAI_API_KEY
)

def classifierAgent(query):
    
    prompt = f'''
    INstructions:
    1. For every input, think about the task, reason it out.
    2. But DO NOT WRITE THE REASONING IN THE OUTPUT. This is just for your thought process.
    3. output should be a single word answer between 'simple' or 'complex'.

    A 'simple' query is a query in which the answer is concise and generating the answer does not require multiple agents.
    It might require multiple tools like web search, case law extractions etc, but the answer is a short answer or a paragraph or two.

    Questions like "Who am I?" or "What is the capital of France?", "What is the stock price of apple", "What was the judgement of a case" etc
    require brief answers. Hence they are classified as 'simple'.

    A 'complex' query is query in which the answer should be a long report covering multiple aspects of the query, it will
    require multiple agents, complex orchestration. 

    Questions like "Analyze the merger between 2 companies", "Compare and contrast 2 resumes", "What are the economic implications of an event",
    "Provide me case laws related to a particular topic", "Give a detailed report on something" etc are classified as 'complex'.

    Your task is to classify the given query is 'simple' or 'complex'. Give a single word answer between 'simple' and 'complex'.

    Following is the query
    {query}
    '''
    messages = [
        {"role": "system", "content": prompt},
    ]
    response = client.chat.completions.create(
        model='gpt-4o-mini', messages=messages, temperature=0
    )
    return response.choices[0].message.content