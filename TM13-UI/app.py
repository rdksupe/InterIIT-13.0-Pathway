from flask import Flask, request, send_file
from flask_cors import CORS
from get_data import get_stock_data,get_data,extract_and_convert_to_json
from convert import convert
import os
app = Flask(__name__)
CORS(app)  

@app.route('/query', methods=['POST'])
def handle_query():
    # Parse the JSON request
    data = request.json
    query = data.get('query', '')

    # Log or process the received query
    print(f"Received query: {query}")
    # get_data(query)
    return '',204


@app.route('/convert', methods=['POST'])
def convert_to_pdf():
    data = request.json
    markdown_content = data.get('content', '')
    print(f"Received markdown content: {markdown_content}")
    markdown_content = str(markdown_content)
    convert(markdown_content)
    if not os.path.exists("generated_output.pdf"):
        return {"error": "Failed to generate PDF"}, 500

    return {"message": "PDF generated successfully"}

@app.route('/download-pdf', methods=['GET'])
def download_pdf():
    output_file = 'generated_output.pdf'

    # Check if the PDF exists
    if not os.path.exists(output_file):
        return {"error": "PDF not found"}, 404

    print("messi")

    return send_file(output_file, as_attachment=True, download_name='generated_output.pdf', mimetype='application/pdf')

if __name__ == '__main__':
    app.run(port=5000, debug=True)  # Run Flask server on port 5000
