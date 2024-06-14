from flask import request, jsonify
from model import db, User, Message

def create_user():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    user = User(username=username, email=email)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201

def create_message():
    data = request.get_json()
    user_id = data.get('user_id')
    content = data.get('content')
    message = Message(user_id=user_id, content=content)
    db.session.add(message)
    db.session.commit()
    return jsonify({'message': 'Message created successfully'}), 201

def get_messages():
    messages = Message.query.all()
    return jsonify([message.content for message in messages]), 200