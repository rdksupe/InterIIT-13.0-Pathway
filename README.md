## Instructions to run Retrieval-Augmented Computational Contextual Organizer with Optimized Navigation


This project requires Python 3.12.0 or later. Ensure that you have the correct Python version installed before running the project.

### For Macintosh
`
brew install libmagic
`

### General Instructions

1. Run the pathway server and rag server by following the instructions in pathway_rag folder
      `
   cd pathway_rag &&
   pip install -r requirements.txt &&
   python3 pw_new.py & python3 rag_server.py
   `

   `
   python3 rag_server.py
   `

2. Run the final backend from the RACCOON folder by the following :
      
   `
   cd RACCOON &&
   pip install -r requirements.txt &&
   python3 main.py
   `
3. Install Required Dependencies and run the UI which will be available at localhost:5173
   
   `
   cd TM13-UI &&
   npm i &&
   npm run dev
   `  
