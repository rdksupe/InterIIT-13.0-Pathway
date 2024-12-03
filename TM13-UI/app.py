from flask import Flask, request
from flask_cors import CORS
from get_data import get_stock_data,get_data,extract_and_convert_to_json
from convert import convert
app = Flask(__name__)
CORS(app)  # Enable CORS to allow requests from the React frontend

@app.route('/query', methods=['POST'])
def handle_query():
    # Parse the JSON request
    data = request.json
    query = data.get('query', '')

    # Log or process the received query
    print(f"Received query: {query}")
    get_data(query)
    # No need to send back any response, just acknowledge
    return '', 204  # 204 No Content indicates success without a body

@app.route('/convert', methods=['POST'])
def convert_to_pdf():
    data = request.json
    markdown_content = data.get('content', '')
    print(f"Received markdown content: {markdown_content}")
    markdown_content = str(markdown_content)
    convert(markdown_content)

if __name__ == '__main__':
    app.run(port=5000, debug=True)  # Run Flask server on port 5000
