import google.generativeai as genai
import os

def classifierAgent(query, api_key):
    prompt = f'''
    A 'simple' query is a query in which the answer is concise and generating the answer does not require multiple agents.
    It might require multiple tools, but the answer is a short answer or a paragraph or two.

    A 'complex' query is query in which the answer should be a long report covering multiple aspects of the query, it will
    require multiple agents, compel orchestration.

    Your task is to classify the given query is 'simple' or 'complex'. Give a single word answer between 'simple' and 'complex'.

    Following is the query
    {query}
    '''
    genai.configure(api_key=api_key)
    #TODO: Add openai here
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text.strip()
