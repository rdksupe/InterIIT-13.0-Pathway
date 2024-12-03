import dotenv
import logging
import os
import google.generativeai as genai
from langchain_experimental.utilities import PythonREPL
from openai import OpenAI
client = OpenAI(api_key="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")
# OpenAI.api_key = os.getenv('OPENAI_API_KEY_30')

def generate_chart(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as md_file:
        content = md_file.read()
    """
    Analyzes a markdown file's content, determines if a chart can be generated, updates the markdown file
    to include the chart, and generates the chart using AI-generated Python code.

    specify the path where the new md file will be saved and the path where the image will be saved
    Args:
        content (str): Content of the markdown file to analyze.

    Returns:
        str: 'Image Saved' if the chart is successfully generated and saved, or an error message otherwise.
    """
    # dotenv.load_dotenv('.env')
    # genai.configure(api_key=os.environ["GEMINI_API_KEY_30"])
    # model = genai.GenerativeModel("gemini-1.5-flash")

    messages = f"""SYSTEM: You are being given a markdown file with the content below. The markdown file contains data extracted from different sources. 
    Your job is to first analyse the data, and find if any kind of potential data visualization can be built for it.\
    If a chart can be built, assume that it is generated and stored in 'assets' folder, with the name of the image being directly related to the data it is presenting. 
    Instructions:

    1. Now simply change the markdown file to include the image at the appropriate place, by mentioning a link to it at the appropriate place. 
    2. Only add a link to include the image and properly define the path of the image in markdown format. Do not change the content at all. 
    3. Do not add charts everywhere. Only add charts if and only if enonugh data is available. Only create charts for numeric data. 
    4. Do not create a graph if in case one of the value is not present for a source. 
    5. Use various different types of graphs available in matplotlib. 
    6. Do not add a markdown code block in the beginnning. 
    """
    # ai_msg = model.generate_content(messages)

    # client = OpenAI()
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": messages},
            {
                "role": "user",
                "content": f"{content}"
            }
        ]
    )

    response = completion.choices[0].message.content.strip()

    file_path = 'response-withCharts.md'
    with open(file_path, 'w', encoding='utf-8') as md_file:
        md_file.write(response)
    print("done")
    repl = PythonREPL()


    messages_new = f"""SYSTEM: You are given content of a markdown file. It contains places where images have been inserted. 
    Your job is to generate the required charts based on the images that have been inserted in the markdown. Make a graph for 
    all the statements which look like:

    ![Heading of Image](path/of/image.png)


    DO NOT GENERATE GRAPHS WHICH ARE NOT INSERTED IN THE MARKDOWN

    1. Use your tools to generate the chart.
    2. Use a non-interactive backend. For example, (matplotlib.use('Agg')). 
    3. Do not view the chart. This is to make sure we avoid this error: NSWindow should only be instantiated on the main thread! 
    4. Do not start Matplotlib GUI.
    5. Save the images in the 'assets' folder. 
    6. Must respond with code directly. 
    7. Do not try to make a code block. 
    8. Just output the python code in plain text.

    Code Guidelines:
    1. Always include
    import matplotlib
    matplotlib.use('Agg')

    Guidelines:
    1. Do not include the punctuations at the starting or end.
    2. Do not include any starter text or header.
    3. Create the required image directory. Assume that it does not exist. 
    4. Successfully save the images to the required directory.
    5. Only create graphs wherever path to the image is defined in the markdown file. If not present, do not create a graph.

    IMPORTANT NOTE: IF THERE ARE MULTIPLE IMAGES INSERTED IN THE MARKDOWN, MAKE A GRAPH CORRESPONDING TO EACH IMAGE INSERTED BASED ON THE DATA NEAR IT.
    WRITE THE CODE SUCH THAT ALL THE IMAGES ARE SAVED AS DIFFERENT IMAGES WITH DESIGNATED NAMES BY RUNNING THE SINGLE PYTHON SCRIPT.
    """

        
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": messages_new},
            {
                "role": "user",
                "content": f"{response}"
            }
        ]
    )

    responsee = completion.choices[0].message.content.strip()
    try:
        result = repl.run(responsee)
        logging.info(f"Execution Result: {result}")
        return "Image Saved"
    except Exception as e:
        logging.error(f"Failed to execute code. Error: {repr(e)}")
        return "Error"


