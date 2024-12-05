# DARTS : DYNAMIC AGENTIC REFLECTIVE TREE SEARCH

## Instructions to run the pipeline


This project requires Python 3.12.0 or later. Ensure that you have the correct Python version installed before running the project. The project also requires npm and node.

### For Macintosh

`
brew install libmagic
`

### General Instructions

1. You have to create 8 terminal instances for each of the following: 4 scripts in pathway_rag folder, (http_serve.py, pw_new.py, pw_userkb.py, rag_server.py). 2 scripts in DARTS folder (main.py and change.py) and 2 scripts in TM13-UI folder (app.py and npm run dev)

2. Spawn 4 terminals and run the scripts in the pathway_rag folder:

   `
   cd pathway_rag &&
   pip install -r requirements.txt &&
   python3 rag_server.py
   `

   `
   cd pathway_rag &&
   python3 pw_new.py
   `

   `
   cd pathway_rag &&
   python3 http_serve.py
   `

   `
   cd pathway_rag &&
   python3 pw_userkb.py
   `
   
4. Spawn 2 terminals and run the scripts in DARTS folder:

   `
   cd RACCOON &&
   pip install -r requirements.txt &&
   python3 main.py
   `

   `
   cd RACCOON &&
   python3 change.py
   `

3. Install Required Dependencies and run the UI which will be available at localhost:517

   `
   cd TM13-UI &&
   python app.py
   `
   
   `
   cd TM13-UI &&
   npm i &&
   npm run dev
   `
