import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ChatbotAI:
    def __init__(self, excel_path, language='English'):
        # Load the appropriate sheet based on the specified language
        if language.lower() == 'english':
            sheet_name = 0  # Assuming the first sheet is in English
        else:
            sheet_name = 1  # Assuming the second sheet is in Vietnamese
        self.df = pd.read_excel(excel_path, sheet_name=sheet_name)
        self.vectorizer = TfidfVectorizer()
        self.question_vectors = self.vectorizer.fit_transform(self.df['Question'])

    def find_most_similar_question(self, user_question):
        user_question_vector = self.vectorizer.transform([user_question])
        similarities = cosine_similarity(user_question_vector, self.question_vectors)
        most_similar_idx = similarities.argmax()
        return self.df.iloc[most_similar_idx]

    def get_answer(self, user_question):
        most_similar_question = self.find_most_similar_question(user_question)
        return most_similar_question['Answer']

# # Example usage for English
# excel_path = "/Users/phamthanhtruc/Downloads/re/Chatbot1/Chatbot-VSTEP.xlsx"
# chatbot_en = ChatbotAI(excel_path, language='English')
# user_question_en = "What does registration for the VSTEP exam include?"
# answer_en = chatbot_en.get_answer(user_question_en)
# print(answer_en)

# # Example usage for Vietnamese
# chatbot_vn = ChatbotAI(excel_path, language='Vietnamese')
# user_question_vn = "Đăng ký tham gia kỳ thi VSTEP bao gồm những gì?"
# answer_vn = chatbot_vn.get_answer(user_question_vn)
# print(answer_vn)

