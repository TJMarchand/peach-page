import json
import os

DATA_FOLDER = os.path.join(os.path.dirname(__file__), 'data')
USER_FILE = os.path.join(DATA_FOLDER, 'users.json')
MESSAGE_FILE = os.path.join(DATA_FOLDER, 'messages.json')
METADATA_FILE = os.path.join(DATA_FOLDER, 'metadata.json')

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
    users[username] = {}
    users[username]['password'] = password
    users[username]['admin'] = "False"
    with open(USER_FILE, 'w') as f:
        json.dump(users, f)
    return True

def verify_user(username, password):
    users = load_users()
    if username not in users:
        return False
    if users[username]["password"] == password:
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
    with open(METADATA_FILE, 'r') as f:
        metadata = json.load(f)
    message_id = metadata["message_id_counter"]
    metadata["message_id_counter"] += 1
    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f)

    messages = load_messages()
    messages.append({'name': name, 'content': content, 'id': message_id})
    with open(MESSAGE_FILE, 'w') as f:
        json.dump(messages, f)

def save_all_messages(messages):
    with open(MESSAGE_FILE, 'w') as f:
        json.dump(messages, f)

def delete_message(message_id):
    messages = load_messages()
    messages = [msg for msg in messages if msg["id"] != message_id]
    print(messages)
    print(message_id)
    print(type(message_id))
    print(type(messages[0]["id"]))
    save_all_messages(messages)