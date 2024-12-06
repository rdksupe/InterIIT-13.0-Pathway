from dotenv import load_dotenv
import logging
import os
import shutil
import google.generativeai as genai
from langchain_experimental.utilities import PythonREPL
import requests
from langchain_openai import ChatOpenAI

load_dotenv('../../.env')
api_gemini = os.getenv("GEMINI_API_KEY_30")
api_img = os.getenv("IMGBB_API_KEY")
openai_api_key=os.getenv("OPEN_AI_API_KEY_30")
GPT4o_mini_GraphGen = ChatOpenAI(model="gpt-4o",openai_api_key = openai_api_key, temperature=0.2, model_kwargs={"top_p": 0.1})


def gen_url(image_paths):
    api_key = api_img  

    url = []
    for image_path in image_paths:

        # Open the image and prepare the file for upload
        with open(image_path, 'rb') as image_file:
            # Define the payload (data) for the API call
            data = {
                'key': api_key,  
                'expiration': '1000',  # Optional, image auto-delete time (in seconds, optional)
            }
            
            files = {
                'image': image_file,  # The image file to be uploaded
            }
            
            # Make the POST request to upload the image
            response = requests.post('https://api.imgbb.com/1/upload', data=data, files=files)

        response_json = response.json()
        if response_json['success']:
            print("Image uploaded successfully!")
            # print(f"Image URL: {response_json['data']['url_viewer']}")
            print(f"Image URL (direct link): {response_json['data']['url']}")
            url.append(response_json['data']['url'])
        else:
            print("Image upload failed!")
            print(response_json)

    return url

def get_paths(response):
    assets_folder = os.path.join(os.getcwd(), 'assets')
    image_paths = []

    for file_name in os.listdir(assets_folder):
        if file_name.endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(assets_folder, file_name)
            image_paths.append(image_path)

    url = gen_url(image_paths)
    # print(url)
    genai.configure(api_key=api_gemini)
    model = genai.GenerativeModel("gemini-1.5-flash")

    message = f"""SYSTEM: you are a helpful AI assistant. you have been given a markdown file. It has images embedded in it. You also have a list of URLs of various images mentioned in the markdown file.
    Your job is to only replace the links of the images with the corresponding URL given. Do not try to change anything else. Return only the full markdown file, without any code block. Only return plain text.
    HUMAN: Markdown : {response}, URLS : {url}"""

    ai_msg = model.generate_content(message)
    file_path = 'response-withCharts.md'
    with open(file_path, 'w', encoding='utf-8') as md_file:
        md_file.write(ai_msg.text)
    return ai_msg.text

def remove_folder_and_contents(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        print(f"Folder '{folder_path}' and its contents have been removed.")
    else:
        print(f"Folder '{folder_path}' does not exist.")



def generate_chart(content: str) -> str:
    assets_folder = os.path.join(os.getcwd(), 'assets')
    remove_folder_and_contents(assets_folder)
    os.mkdir(assets_folder)
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
    3. Do not add charts everywhere. Only add charts if and only if enough data is available. Only create charts for numeric data. 
    4. Do not create a graph if in case one of the value is not present for a source. 
    5. Use various different types of graphs available in matplotlib. 
    6. Do not add a markdown code block in the beginning. 
    """

    #TODO: Add gemini-1.5-flash model
    '''completion = client.chat.completions.create(
        model=os.getenv("MODEL_NAME"),
        messages=[
            {"role": "system", "content": messages},
            {
                "role": "user",
                "content": f"{content}"
            }
        ]
    )

    response_text = completion.choices[0].message.content.strip()'''

    response_text = GPT4o_mini_GraphGen.invoke(f'''{messages}\n\n {content}''').content

    file_path = 'response-withCharts.md'
    with open(file_path, 'w', encoding='utf-8') as md_file:
        md_file.write(response_text)
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

        
    '''completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": messages_new},
            {
                "role": "user",
                "content": f"{response}"
            }
        ]
    )

    response = completion.choices[0].message.content.strip()'''

    response = GPT4o_mini_GraphGen.invoke(f'''{messages_new}\n\n {response_text}''').content

    with open('code.txt', 'w') as f:
        f.write(response)

    try:
        result = repl.run(response)
        logging.info(f"Execution Result: {result}")
        return get_paths(response_text)
    except Exception as e:
        logging.error(f"Failed to execute code. Error: {repr(e)}")
        return f"Error {e}"


if __name__ == '__main__':
    print(generate_chart(
        """# Comprehensive Report on the Impact of Telecom Mergers on Regulatory Policies and Digital Inclusion Initiatives in Rural India

## Introduction

The telecommunications sector in India has witnessed significant changes, particularly with the emergence of Reliance Jio as a dominant player since its inception in 2016. With over 481.8 million subscribers as of March 2024, Jio has transformed the landscape of digital services in India, focusing on enhancing digital inclusion across various demographics, particularly in rural regions. This report analyzes how potential mergers in the telecom sector could affect regulatory policies and initiatives aimed at enhancing digital inclusion in rural India.

## Overview of Telecom Landscape in India

The Indian telecom sector is characterized by intense competition, with Reliance Jio leading the market. As of FY 2023-24, Jio reported revenues exceeding ₹100,000 crore and an EBITDA of ₹50,000 crore, underscoring its financial strength (Reliance Jio Infocomm Limited Annual Report 2024, p. 6). The company's robust network coverage extends to 99% of the Indian population, including hard-to-reach terrains and remote villages, which traditionally lack digital access (Reliance Jio Infocomm Limited Annual Report 2024, p. 65).

### Digital Inclusion Initiatives

Jio's commitment to digital inclusion is evident through various initiatives aimed at providing affordable services and enhancing digital skills. The company has aligned its mobile applications with the Web Content Accessibility Guidelines (WCAG) version 2.1, achieving AA level conformance for popular applications (Reliance Jio Infocomm Limited Annual Report 2024, p. 65). Furthermore, Jio's WomenConnect Challenge, launched in partnership with USAID, aims to empower women by improving access to digital technology, impacting over 300,000 women across India (Reliance Jio Infocomm Limited Annual Report 2024, p. 65).

## Impact of Telecom Mergers on Regulatory Policies

### 1. Market Consolidation and Competition

The potential merger of telecom companies could lead to market consolidation, affecting competition. Regulatory bodies, such as the Telecom Regulatory Authority of India (TRAI), may need to revise policies to prevent monopolistic practices and ensure fair competition. A consolidated market could lead to increased pricing power for the merged entity, which may hinder the affordability of services crucial for digital inclusion.

#### SWOT Analysis of Potential Mergers

| Strengths                        | Weaknesses                     |
|----------------------------------|--------------------------------|
| Increased operational efficiency  | Potential for reduced competition |
| Enhanced technological capabilities | Risk of service monopolization  |
| Greater financial resources       | Regulatory scrutiny and delays  |

| Opportunities                    | Threats                        |
|----------------------------------|--------------------------------|
| Expansion of digital services     | Regulatory pushback            |
| Enhanced investment in rural areas | Consumer backlash against pricing |

### 2. Regulatory Scrutiny and Compliance

Mergers in the telecom sector would attract heightened scrutiny from regulatory bodies. The Competition Commission of India (CCI) would evaluate the merger's impact on market competition and consumer welfare. Regulatory compliance costs may increase, diverting resources away from digital inclusion initiatives.

### 3. Policy Framework for Digital Inclusion

The merger could necessitate the formulation of new policies or the revision of existing ones aimed at promoting digital inclusion. Regulatory bodies may impose conditions on merged entities to maintain service affordability and accessibility, particularly in rural areas. 

### 4. Funding and Investment in Infrastructure

Mergers could lead to increased capital for investment in infrastructure, particularly in underserved rural regions. However, the focus on profitability may overshadow the need for investment in digital inclusion initiatives. Regulatory frameworks may need to incentivize investments in rural infrastructure to ensure that the benefits of mergers extend to underserved populations.

## Case Studies of Previous Mergers

### Case Study 1: Vodafone-Idea Merger

The merger between Vodafone India and Idea Cellular in 2018 aimed to create the largest telecom operator in India. While the merger resulted in improved operational efficiencies and a broader customer base, it also led to increased tariffs, impacting affordability for consumers (Source: TRAI Report, 2020).

### Case Study 2: Bharti Airtel and Telenor India

Bharti Airtel's acquisition of Telenor India in 2017 expanded its subscriber base and strengthened its market position. However, the merger raised concerns regarding competition and service quality, prompting regulatory scrutiny (Source: CCI Report, 2018).

## Regulatory Initiatives for Digital Inclusion

### 1. National Digital Communications Policy (NDCP) 2018

The NDCP aims to provide universal broadband access, enhance digital infrastructure, and promote digital literacy. Mergers could align with this policy, but regulatory bodies must ensure that merged entities adhere to the principles of affordability and accessibility in their service offerings.

### 2. Digital India Initiative

The Digital India initiative focuses on transforming India into a digitally empowered society. Regulatory bodies may need to enforce compliance measures to ensure that merged telecom entities contribute to this initiative, particularly in rural areas.

### 3. Universal Service Obligation Fund (USOF)

The USOF aims to provide financial support for expanding telecom services in rural and remote areas. Mergers may necessitate contributions from merged entities to the USOF, ensuring that digital inclusion remains a priority.

## Conclusion

The merger of telecom companies in India has the potential to significantly impact regulatory policies and initiatives aimed at enhancing digital inclusion in rural regions. While consolidation may lead to operational efficiencies and increased investment, it also poses risks related to competition, affordability, and service quality. Regulatory bodies must adopt a proactive approach to ensure that the benefits of mergers extend to underserved populations, promoting digital inclusion as a priority.

### Key Takeaways

1. **Regulatory Scrutiny**: Mergers will attract scrutiny from regulatory bodies, necessitating compliance with competition and consumer welfare standards.
  
2. **Investment in Infrastructure**: Mergers could provide increased capital for infrastructure investment, but regulatory frameworks must incentivize investments in rural areas.

3. **Policy Alignment**: Merged entities must align with national policies aimed at promoting digital inclusion, ensuring that affordability and accessibility remain priorities.

### Next Steps

1. **Monitoring and Evaluation**: Regulatory bodies should establish mechanisms for monitoring the impact of mergers on service affordability and accessibility.

2. **Stakeholder Engagement**: Engaging with stakeholders, including consumers and rural communities, will be essential to understand the implications of mergers on digital inclusion.

3. **Policy Development**: Developing policies that promote digital inclusion as a core principle of telecom mergers will be crucial in ensuring equitable access to digital services across India.

### References

- Reliance Jio Infocomm Limited Annual Report 2024, pp. 6, 65.
- TRAI Report, 2020.
- CCI Report, 2018.

![Telecom Market Revenue and EBITDA](assets/telecom_market_revenue_ebitda.png)
"""
    ))