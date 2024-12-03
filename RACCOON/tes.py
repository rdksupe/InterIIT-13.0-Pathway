import os
from dotenv import load_dotenv
print(load_dotenv('.env'))

api_key = os.getenv('OPEN_AI_API_KEY_30')
print(api_key)