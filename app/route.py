from flask import Blueprint
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