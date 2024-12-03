from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
load_dotenv('.env')

openai_api_key=os.getenv("OPENAI_API_KEY_30")

llm_to_check = ChatOpenAI(model="gpt-4o-mini",openai_api_key = openai_api_key, temperature=0.2)