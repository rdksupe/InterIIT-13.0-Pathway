import yfinance as yf
import dotenv
import logging
import os
import json
import google.generativeai as genai
from langchain_huggingface import HuggingFaceEndpoint
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import json
import re
from openai import OpenAI
client = OpenAI(api_key="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")

def extract_and_convert_to_json(text):
    # Using regex to find the company name and ticker symbol pattern
    pattern = r'"company_name":\s*"([^"]+)",\s*"ticker_symbol":\s*"([^"]+)"'
    
    # Find all matches for company data
    matches = re.findall(pattern, text)
    
    # Prepare a list of dictionaries for the JSON structure
    companies = []
    for match in matches:
        company = {
            "company_name": match[0],
            "ticker_symbol": match[1],
            "file_path": f"src/{match[0]}_stock_data.csv"
        }
        companies.append(company)
    
    # Create a valid JSON structure
    json_data = json.dumps(companies, indent=4)
    
    # Save it to a JSON file
    with open('companies.json', 'w') as f:
        f.write(json_data)
    
    print(json_data)


logging.basicConfig(level=logging.INFO)
def get_data(query : str):

    message = f"""SYSTEM: You are a helpful AI assistant. You are being given a query. Your job is to extract the names of the company and their ticker symbols so that data from yfinance can be scrapped.
    Return your answer in a JSON format in the following format:
    [
        [
            "company_name": "Apple Inc.",
            "ticker_symbol": "AAPL"
        ]
    ]
    
    Do not return any other redundant information. Only return the company name and the ticker symbol, as mentioned above. Do not give any code block. Only return plain text. Do not write json on the top. Give details for all comapnies mentioed in the query. Do not return any other information. Make sure the company name does not have any kinf of spaces in betweem.

    """

    # repo_id = "meta-llama/Meta-Llama-3-8B-Instruct"
    # llm = HuggingFaceEndpoint(repo_id = repo_id , temperature = 0.5)
    # output = llm.invoke(message)
    completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": message},
                {
                    "role": "user",
                    "content": f"{query}"
                }
            ]
        )

    output = completion.choices[0].message.content.strip()
    extract_and_convert_to_json(output)

def get_stock_data(ticker_symbol, start_date, end_date, output_file):
    stock = yf.Ticker(ticker_symbol)
    df = stock.history(start=start_date, end=end_date)
    
    df.to_csv(output_file)
    return df

query = "Give me a detailed report on the impacts of Alibaba acquiring eBay  . Would that be a reasonable acquisition? If so, what are the potential consequences of that company from a financial and consumer based perspective."
get_data(query)

# Read the companies.json file
with open('companies.json', 'r') as f:
    companies_data = json.load(f)

# Loop through each company
for company in companies_data:
    ticker_symbol = company['ticker_symbol']
    company_name = company['company_name']
    
    # Call the get_stock_data function for the current company
    start_date = '2023-05-01'
    end_date = '2024-11-30'
    output_file = f'src/{company_name}_stock_data.csv'
    get_stock_data(ticker_symbol, start_date, end_date, output_file)
