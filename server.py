from flask import Flask, request, jsonify
from exc import ChatbotAI  
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)

# After initializing your Flask app
CORS(app)

# Initialize chatbot instances for English and Vietnamese
excel_path = "Chatbot-VSTEP.xlsx" 
chatbot_en = ChatbotAI(excel_path, language='English')
chatbot_vn = ChatbotAI(excel_path, language='Vietnamese')

@app.route('/')
def home():
    return app.send_static_file('index.html')

@app.route('/query/', methods=['POST'])
def query():
    data = request.json
    question = data.get('query', '')

    # Simple language detection based on the presence of Vietnamese characters
    if any("ăâđêôơư" in s for s in question.lower()):
        answer = chatbot_vn.get_answer(question)
    else:
        answer = chatbot_en.get_answer(question)

    return jsonify({'response': answer})

if __name__ == '__main__':
    app.run(debug=True)