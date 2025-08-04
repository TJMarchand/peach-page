import json
import os

DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'messages.json')

def load_messages():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_message(name, content):
    messages = load_messages()
    messages.append({'name': name, 'content': content})
    with open(DATA_FILE, 'w') as f:
        json.dump(messages, f)
