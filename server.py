from flask import Flask, request, jsonify
from exc import ChatbotAI  
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

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

    # Enhanced language detection logic
    def is_vietnamese(question):
        # Vietnamese-specific characters
        vietnamese_chars = "ủũụọõỏẹẻẽịĩỉìạãảàăâđêôơưđ"
        # Common Vietnamese words or phrases without accents
        vietnamese_keywords = ['la', 'ai', 'bao', 'nao', 'dau', 'cua', 'gi', 'ban', 'toi', 'minh', 'khong', 'nhe', 'co', 'thi', 'thoi', 'the'] # 'ue', 'oi', 'oe', 'ua'
        
        question_lower = question.lower()
        # Check for Vietnamese-specific characters
        if any(char in vietnamese_chars for char in question_lower):
            return True
        # Check for common Vietnamese words or phrases
        elif any(keyword in question_lower for keyword in vietnamese_keywords):
            return True
        return False

    if is_vietnamese(question):
        answer = chatbot_vn.get_answer(question)
    else:
        answer = chatbot_en.get_answer(question)

    return jsonify({'response': answer})

if __name__ == '__main__':
    app.run(debug=True) 
