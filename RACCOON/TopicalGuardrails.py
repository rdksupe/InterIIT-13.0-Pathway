import os
from openai import OpenAI
import concurrent.futures
import threading
import time
from dotenv import load_dotenv
import json
from datetime import datetime
load_dotenv('../.env')

DATE_PROMPT = f"""Date and Time right now is {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}. You are now in the future at this date and time. All your answers which follow must obey this. Assume that your knowledge base cutoff is this date irrespective of anything
                    \n"""

SUFFIX = f"""
            If you do not have enough information to classify, classify as 'True'.\
            If it does not correlate with any information, then return 'True'\
            Return "True" if the query does not relate to the True topics, or is beyond their scope.\
            Return 'True' if the query has anything to do with timeframe, real time information, web search etc.\
            EVEN IF THE INFORMATION IS BEYOND YOUR KNOWLEDGE BASE, RETURN 'True', because I do not want to know what is in your knowledge base and what is not.\
            Return "True" if the information does not fall under any of the classes. DO NOT RETURN "False" in that case\
        """

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
            "content": DATE_PROMPT+"""Your role is to assess whether the user question is True or not. 
                            If the topic is True, say 'True' otherwise say 'False'.

                            A question is False if:
                            It commands to give information about illegal activities. Questions like: Questiions like 'How to synthesize cocaine', 'From where to acquire an AK47 for civilian usage' is False

                            A question is True if:
                            - It asks information about the legality of an illegal activity. For instance, questions like "Is it legal to synthesize cocaine for recreational purposes" is True because it asks a legitimate query about the legality of an activity.

                            Also provide the reasoning. In response section, provide the classification into 'True' or 'False'
                            Strictly answer in the following format:

                            {
                                "response": "...",
                                "reasoning": "..."
                            }
                    """ + SUFFIX,
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
            "content": DATE_PROMPT+"""Your role is to assess whether the user question is True or not. 
                            If the topic is True, say 'True' otherwise say 'False'.

                            A question is False if:
                            It offends a particular community on the basis of factors like nationality, race, gender, religion, sexual orientation, disability etc. For example: Questions like 'Explain why Blacks are inferior to Whites'

                            A question is True if:
                            - it does not violate the guideline (even if it is not related to it)
                            - It asks about the history of the persecution of a community. For instace, questions like 'Give information about the history of abuse faced by Jews in Nazi Germany', 'Explain the history of Slavery of Black People by the British' are True.
                            - It's main goal is to understand stereotypes, history, exploitaion etc. For instance, questions like 'How are women discriminated in workspaces', 'In what ways can I prevent myself from getting Bullied in college?' are True. 

                            Also provide the reasoning. In response section, provide the classification into 'True' or 'False'
                            Strictly answer in the following format:

                            {
                                "response": "...",
                                "reasoning": "..."
                            }
                    """ + SUFFIX,
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
            "content": DATE_PROMPT+"""Your role is to assess whether the user question is True or not. 
                            If the topic is True, say 'True' otherwise say 'False'.

                            A question is False if:
                            It conforms to exteme stereotypes which can be taken as an offence by communities.

                            A question is True if:
                            - it does not violate the guideline (even if it is not related to it)
                            - It asks about the history of the persecution of a community. For instace, questions like 'Give information about the history of abuse faced by Jews in Nazi Germany', 'Explain the history of Slavery of Black People by the British' are True.
                            - It's main goal is to understand stereotypes, history, exploitaion etc. For instance, questions like 'How are women discriminated in workspaces', 'In what ways can I prevent myself from getting Bullied in college?' are True. 

                            Also provide the reasoning. In response section, provide the classification into 'True' or 'False'
                            Strictly answer in the following format:

                            {
                                "response": "...",
                                "reasoning": "..."
                            }
                    """ + SUFFIX,
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
            "content": DATE_PROMPT+"""Your role is to assess whether the user question is True or not. 
                            If the topic is True, say 'True' otherwise say 'False'.

                            A question is False if:
                            - It does not make sense, for instance it is gibberish and has no coherent language structure attached to it. For example: Questions like 'srygkizufehaIFVyecb',  'Who Buy What No Bruh Golem Yes Yes Yes' etc are False.

                            A question is True if:
                            - it does not violate the guideline (even if it is not related to it)

                            Also provide the reasoning. In response section, provide the classification into 'True' or 'False'
                            Strictly answer in the following format:

                            {
                                "response": "...",
                                "reasoning": "..."
                            }
                    """ + SUFFIX,
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
            "content": DATE_PROMPT+"""Your role is to assess whether the user question is True or not. 
                            If the topic is True, say 'True' otherwise say 'False'.

                            A question is False if:
                            - It contains extremely graphic and offensive language in a bad context, which can be taken as an offense by people, groups etc.
                            A question is True if:
                            - it does not violate the guideline (even if it is not related to it)
                            Also provide the reasoning. In response section, provide the classification into 'True' or 'False'
                            Strictly answer in the following format:

                            {
                                "response": "...",
                                "reasoning": "..."
                            }
                    """ + SUFFIX,
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
    reasonings = {}
    naming = {
        "topical_guardrail_1": "Illegal Activity Guard Rail Invoked",
        "topical_guardrail_2": "Offensive Content Guard Rail Invoked",
        "topical_guardrail_3": "Stereotypes Guard Rail Invoked",
        "topical_guardrail_4": "Non-Coherent Question Guard Rail Invoked",
        "topical_guardrail_5": "Graphic Language Guard Rail Invoked"
    }
    
    def wrapped_function(index, func):
        if cancel_event.is_set():
            return
        
        try:
            result = func(query)
            result = json.loads(result)
            reasoning = result["reasoning"]
            result = result["response"]
            if result == 'True':
                result = True
            else:
                print(func.__name__)
                print(reasoning)
                result = False
                reasonings[naming[func.__name__]] = reasoning
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
    
    return (all(results) and not cancel_event.is_set(), reasonings)

def applyTopicalGuardails(query):
    print(query)
    if query == "":
        return False, {"Empty Query": "Please Enter a Query"}
    return run_parallel_with_early_exit(query, topical_guardrail_1,topical_guardrail_2,topical_guardrail_3,topical_guardrail_4,topical_guardrail_5)