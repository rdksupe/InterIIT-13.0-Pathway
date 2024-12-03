# DARTS : DYNAMIC AGENTIC REFLECTIVE TREE SEARCH

## Instructions to run the pipeline


This project requires Python 3.12.0 or later. Ensure that you have the correct Python version installed before running the project. The project also requires npm and node.

### For Macintosh

`
brew install libmagic
`

### General Instructions

1. Create 2 python environments: One for pathway_rag, and the other for RACCOON. Let the environment for pathway_rag be named PathwayEnv and the environment for RACCOON be named RacEnv.

2. You have to create 4 terminal instances for each of the following: RAG server, Pathway server, RACCOON and frontend. RAG server, Pathway server will be run on the PathwayEnv and RACCOON will be run on RacEnv.

3. Run the pathway server and rag server by following the instructions in pathway_rag folder
   `
   cd pathway_rag &&
   pip install -r requirements.txt &&
   python3 rag_server.py
   `

3. Run the pathway server and rag server by following the instructions in pathway_rag folder
   `
   cd pathway_rag &&
   pip install -r requirements.txt &&
   python3 pw_new.py
   `

4. For running RACCOON:
   `
   cd RACCOON &&
   pip install -r requirements.txt &&
   python3 main.py
   `

3. Install Required Dependencies and run the UI which will be available at localhost:5173
   `
   cd TM13-UI &&
   python app.py &&
   npm i &&
   npm run dev
   `
