import json
import os

DATA_FOLDER = os.path.join(os.path.dirname(__file__), 'data')
USER_FILE = os.path.join(DATA_FOLDER, 'users.json')
MESSAGE_FILE = os.path.join(DATA_FOLDER, 'messages.json')

def load_users():
    try:
        with open(USER_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    
def save_user(username, password):
    users = load_users()
    if username in users:
        return False    # User already exists.
    users[username] = password
    with open(USER_FILE, 'w') as f:
        json.dump(users, f)
    return True

def verify_user(username, password):
    users = load_users()
    if username not in users:
        return False
    if users[username] == password:
        return True
    else:
        return False

def load_messages():
    try:
        with open(MESSAGE_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_message(name, content):
    messages = load_messages()
    messages.append({'name': name, 'content': content})
    with open(MESSAGE_FILE, 'w') as f:
        json.dump(messages, f)
