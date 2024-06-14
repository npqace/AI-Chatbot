from flask import Blueprint, request, jsonify
from controller import create_user, create_message, get_messages

api = Blueprint('api', __name__)

@api.route('/user', methods=['POST'])
def new_user():
    return create_user()

@api.route('/message', methods=['POST'])
def new_message():
    return create_message()

@api.route('/messages', methods=['GET'])
def all_messages():
    return get_messages()

@api.route('/predict', methods=['POST'])
def predict():
    # Extract data from request
    data = request.json
    
    # Perform prediction (this is just a placeholder, replace with your logic)
    prediction = "This is where you would return the prediction result."
    
    # Return the prediction as a JSON response
    return jsonify({'prediction': prediction})