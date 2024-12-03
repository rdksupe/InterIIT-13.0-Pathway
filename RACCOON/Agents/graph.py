import dotenv
import logging
import os
import google.generativeai as genai
from langchain_experimental.utilities import PythonREPL


def generate_chart(content: str) -> str:
    """
    Analyzes a markdown file's content, determines if a chart can be generated, updates the markdown file
    to include the chart, and generates the chart using AI-generated Python code.

    specify the path where the new md file will be saved and the path where the image will be saved
    Args:
        content (str): Content of the markdown file to analyze.

    Returns:
        str: 'Image Saved' if the chart is successfully generated and saved, or an error message otherwise.
    """
    dotenv.load_dotenv('.env')
    genai.configure(api_key=os.environ["GEMINI_API_KEY_30"])
    model = genai.GenerativeModel("gemini-1.5-flash")

    messages = f"""SYSTEM: You are a helpful AI assistant. You are being given a markdown file with the content below. The markdown file contains data extracted from different sources. Your job is to first analyse the data, and find if any kind of potential data visualization can be built for it.\
    If a chart can be built, assume that it is generated and stored in 'assets' folder, with the name of the image being directly related to the data it is presenting. Now simply change the markdown file to include the image at the appropriate place. Only add a link to include the image. Do not change the content at all. Do not add charts everywhere. Only add charts if and only if enonugh data is available. Do not create a graph if in case one of the value is not present for a source. Use various different types of graphs available in matplotlib. Do not add a markdown code block in the beginnning.\ 
    HUMAN: {content}
    """
    ai_msg = model.generate_content(messages)

    file_path = 'gold.md'
    with open(file_path, 'w', encoding='utf-8') as md_file:
        md_file.write(ai_msg.text)
    print("done")
    repl = PythonREPL()


    messages_new = f"""SYSTEM: You are a helpful AI assistant. You are given content of a markdown file. It contains places where images have been inserted. Your job is to generate the required charts, using the data present in the content of the file. 
      Your job is to generate a chart based on the instructions provided. Use your tools to generate the chart.
    Use a non-interactive backend. For example, (matplotlib.use('Agg')). Do not view the chart. This is to make sure we avoid this error: NSWindow should only be instantiated on the main thread! Do not start Matplotlib GUI.
    Save the image to the required correct folder. Must respond with code directly. Do not try to make a code block. Just output the python code.

    Code Guidelines:
    1. Always include
    import matplotlib
    matplotlib.use('Agg')

    Guidelines:
    1. Do not include the punctuations at the starting or end.
    2. Do not include any starter text or header.
    3. Create the required image directory. Assume that it does not exist. 
    4. Successfully save the image to the required directory.
    HUMAN: {ai_msg.text}
    """
    final = model.generate_content(messages_new)
    # logging.info(f"Python_Tool: AI_CODE respone: {ai_msg.text}")
    print(final.text)
    # Execute the generated code and log the result
    try:
        result = repl.run(final.text)
        logging.info(f"Execution Result: {result}")
        return "Image Saved"
    except Exception as e:
        logging.error(f"Failed to execute code. Error: {repr(e)}")
        return "Error"


    
file_path = 'drafted_response.md'

# Open the file in read mode
with open(file_path, 'r', encoding='utf-8') as md_file:
    # Read the content
    content = md_file.read()

generate_chart(content)
