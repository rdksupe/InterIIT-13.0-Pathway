## For Running UI

1. Install Required Dependencies and run the UI which will be available at localhost:5173
   
   `
   cd TM13-UI &&
   npm i &&
   npm run dev
   `
2. Run the pathway server and rag server by following the instructions in pathway_rag folder
      `
   cd pathway_rag &&
   pip install -r requirements.txt &&
   python3 pw_new.py & python3 rag_server.py
   `

4. Run the final backend from the RACCOON folder by the following :
      
   `
   cd RACCOON &&
   pip install -r requirements.txt &&
   python3 main.py
   `
   
