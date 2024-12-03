import os
from openai import OpenAI
import concurrent.futures
import threading
import time
from dotenv import load_dotenv
load_dotenv('../.env')

system_prompt = "You are a helpful assistant."

OPENAI_API_KEY = os.getenv('OPEN_AI_API_KEY_30')

client = OpenAI(
    api_key=OPENAI_API_KEY
)

def get_chat_response(user_request):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_request},
    ]
    response = client.chat.completions.create(
        model='gpt-4o-mini', messages=messages, temperature=0.5
    )

    return response.choices[0].message.content

def topical_guardrail_1(user_request):
    messages = [
        {
            "role": "system",
            "content": """Your role is to assess whether the user question is allowed or not. 
                            If the topic is allowed, say 'allowed' otherwise say 'not_allowed'.

                            A question is not allowed if:
                            It commands to give information about illegal activities. Questions like: Questiions like 'How to synthesize cocaine', 'From where to acquire an AK47 for civilian usage' is not allowed

                            A question is ALLOWED if:
                            - it does not violate the guideline (even if it is not related to it)
                            - It asks information about the legality of an illegal activity. For instance, questions like "Is it legal to synthesize cocaine for recreational purposes" is allowed because it asks a legitimate query about the legality of an activity.
                    """,
        },
        {"role": "user", "content": user_request},
    ]
    response = client.chat.completions.create(
        model='gpt-4o-mini', messages=messages, temperature=0
    )

    return response.choices[0].message.content

def topical_guardrail_2(user_request):
    messages = [
        {
            "role": "system",
            "content": """Your role is to assess whether the user question is allowed or not. 
                            If the topic is allowed, say 'allowed' otherwise say 'not_allowed'.

                            A question is not allowed if:
                            It offends a particular community on the basis of factors like nationality, race, gender, religion, sexual orientation, disability etc. For example: Questions like 'Explain why Blacks are inferior to Whites'

                            A question is ALLOWED if:
                            - it does not violate the guideline (even if it is not related to it)
                            - It asks about the history of the persecution of a community. For instace, questions like 'Give information about the history of abuse faced by Jews in Nazi Germany', 'Explain the history of Slavery of Black People by the British' are ALLOWED.
                            - It's main goal is to understand stereotypes, history, exploitaion etc. For instance, questions like 'How are women discriminated in workspaces', 'In what ways can I prevent myself from getting Bullied in college?' are ALLOWED. 
                    """,
        },
        {"role": "user", "content": user_request},
    ]
    response = client.chat.completions.create(
        model='gpt-4o-mini', messages=messages, temperature=0
    )

    return response.choices[0].message.content

def topical_guardrail_3(user_request):
    messages = [
        {
            "role": "system",
            "content": """Your role is to assess whether the user question is allowed or not. 
                            If the topic is allowed, say 'allowed' otherwise say 'not_allowed'.

                            A question is not allowed if:
                            It conforms to exteme stereotypes which can be taken as an offence by communities.

                            A question is ALLOWED if:
                            - it does not violate the guideline (even if it is not related to it)
                            - It asks about the history of the persecution of a community. For instace, questions like 'Give information about the history of abuse faced by Jews in Nazi Germany', 'Explain the history of Slavery of Black People by the British' are ALLOWED.
                            - It's main goal is to understand stereotypes, history, exploitaion etc. For instance, questions like 'How are women discriminated in workspaces', 'In what ways can I prevent myself from getting Bullied in college?' are ALLOWED. 
                    """,
        },
        {"role": "user", "content": user_request},
    ]
    response = client.chat.completions.create(
        model='gpt-4o-mini', messages=messages, temperature=0
    )

    return response.choices[0].message.content

def topical_guardrail_4(user_request):
    messages = [
        {
            "role": "system",
            "content": """Your role is to assess whether the user question is allowed or not. 
                            If the topic is allowed, say 'allowed' otherwise say 'not_allowed'.

                            A question is not allowed if:
                            - it does not violate the guideline (even if it is not related to it)
                            - It does not make sense, for instance it is gibberish and has no cohesive language structure attached to it. For example: Questions like 'srygkizufehaIFVyecb',  'Who Buy What No Bruh Golem Yes Yes Yes' etc are not allowed.
                    """,
        },
        {"role": "user", "content": user_request},
    ]
    response = client.chat.completions.create(
        model='gpt-4o-mini', messages=messages, temperature=0
    )

    return response.choices[0].message.content

def topical_guardrail_5(user_request):
    messages = [
        {
            "role": "system",
            "content": """Your role is to assess whether the user question is allowed or not. 
                            If the topic is allowed, say 'allowed' otherwise say 'not_allowed'.

                            A question is not allowed if:
                            - it does not violate the guideline (even if it is not related to it)
                            - It contains extremely graphic and offensive language in a bad context, which can be taken as an offense by people, groups etc.
                    """,
        },
        {"role": "user", "content": user_request},
    ]
    response = client.chat.completions.create(
        model='gpt-4o-mini', messages=messages, temperature=0
    )

    return response.choices[0].message.content

def run_parallel_with_early_exit(query, *functions):
    cancel_event = threading.Event()
    results = [None] * len(functions)
    
    def wrapped_function(index, func):
        if cancel_event.is_set():
            return
        
        try:
            result = func(query)
            if result == 'allowed':
                result = True
            else:
                result = False
            results[index] = result
            
            if result is False:
                cancel_event.set()
        except Exception as e:
            print(e)
            results[index] = False
            cancel_event.set()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(functions)) as executor:
        futures = [
            executor.submit(wrapped_function, i, func) 
            for i, func in enumerate(functions)
        ]
        
        concurrent.futures.wait(futures)
    
    return all(results) and not cancel_event.is_set()

def applyTopicalGuardails(query):
    return run_parallel_with_early_exit(query, topical_guardrail_1,topical_guardrail_2,topical_guardrail_3,topical_guardrail_4,topical_guardrail_5)