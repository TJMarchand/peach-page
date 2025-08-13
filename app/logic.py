# app/logic.py
"""
Data access layer for the Peach Page toy forum.
"""

from typing import Any, Dict, List, Optional
import json
import os
import tempfile

BASE_DIR = os.path.dirname(__file__)
DATA_FOLDER = os.path.join(BASE_DIR, "data")
USER_FILE = os.path.join(DATA_FOLDER, 'users.json')
MESSAGE_FILE = os.path.join(DATA_FOLDER, 'messages.json')
METADATA_FILE = os.path.join(DATA_FOLDER, 'metadata.json')

DEFAULT_USERS: Dict[str, Dict[str, Any]] = {}
DEFAULT_MESSAGES: Dict[str, List[Dict[str, Any]]] = {
    "Home": [{"name": "Peach", "content": "Welcome to Peach page!", "id": 0}]
}
DEFAULT_METADATA: Dict[str, Any] = {
    "message_id_counters": {"Home": 1},  # 'Home' already used id 0
    "current_thread": "Home"
}



# ----------------------------------------------------------------------------
#                               Low-level helpers
# ----------------------------------------------------------------------------

def _ensure_data_folder_exists() -> None:
    os.makedirs(DATA_FOLDER, exist_ok=True)


def _atomic_write_json(path: str, data: Any) -> None:
    """
    Write JSON to a temporary file in the same directory then atomically replace the target file.
    This reduces the chance of ending up with partial/corrupt JSON on crashes.
    """
    dirpath = os.path.dirname(path) or "."
    _ensure_data_folder_exists()
    # NamedTemporaryFile with delete=False so we can replace after writing
    with tempfile.NamedTemporaryFile("w", dir=dirpath, delete=False, encoding="utf-8") as tf:
        json.dump(data, tf, indent=2, ensure_ascii=False)
        temp_name = tf.name
    os.replace(temp_name, path)


def _load_json_with_default(path: str, default: Any) -> Any:
    """Load JSON; if missing or invalid, create file with default and return default."""
    _ensure_data_folder_exists()
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # create file with default contents
        _atomic_write_json(path, default)
        return default


# ----------------------------------------------------------------------------
#                                     USERS
# ----------------------------------------------------------------------------

def load_users() -> Dict[str, Dict[str, Any]]:
    return _load_json_with_default(USER_FILE, DEFAULT_USERS)


def save_users(users: Dict[str, Dict[str, Any]]) -> None:
    _atomic_write_json(USER_FILE, users)
    

def save_user(username: str, password: str, admin: bool = False) -> bool:
    """
    Create a new user. Returns True on success, False if user exists.
    NOTE: passwords are stored in plain text here (toy project).
    """
    users = load_users()
    if username in users:
        return False
    users[username] = {"password": password, "admin": admin}
    save_users(users)
    return True


def verify_user(username: str, password: str) -> bool:
    users = load_users()
    user = users.get(username)
    return bool(user and user.get("password") == password)


def is_admin(username: Optional[str]) -> bool:
    if not username:
        return False
    users = load_users()
    # .get returns the value of the given key.
    # If the key does not exist, returns the default (second argument, here {}).
    return bool(users.get(username, {}).get("admin", False))

# ----------------------------------------------------------------------------
#                                THREADS / MESSAGES
# ----------------------------------------------------------------------------
def load_messages() -> Dict[str, List[Dict[str, Any]]]:
    return _load_json_with_default(MESSAGE_FILE, DEFAULT_MESSAGES)


def save_all_messages(messages: Dict[str, List[Dict[str, Any]]]) -> None:
    _atomic_write_json(MESSAGE_FILE, messages)


def load_metadata() -> Dict[str, Any]:
    return _load_json_with_default(METADATA_FILE, DEFAULT_METADATA)


def save_metadata(metadata: Dict[str, Any]) -> None:
    _atomic_write_json(METADATA_FILE, metadata)


def get_threads() -> List[str]:
    messages = load_messages()
    return list(messages.keys()) # return stable list (convert from dict_keys)


def get_current_thread() -> Optional[str]:
    metadata = load_metadata()
    return metadata.get("current_thread")


def get_messages_for_thread(thread: Optional[str] = None) -> List[Dict[str, Any]]:
    messages = load_messages()
    if thread is None:
        thread = get_current_thread()
    if not thread:
        return []
    return messages.get(thread, [])


def set_current_thread(thread: str) -> None:
    """
    Switch current thread.
    """
    metadata = load_metadata()
    metadata["current_thread"] = thread
    save_metadata(metadata)


def save_message(author: str, content: str, thread: Optional[str] = None) -> int:
    """
    Save a message and return its message id.
    """
    metadata = load_metadata()
    if thread is None:
        thread = metadata.get("current_thread")
    if thread is None:
        raise ValueError("No thread specified and no current thread set.")

    messages = load_messages()
    # .setdefault returns the value of the key (messages["thread"]) if the key exists.
    # If the key does not exist, it inserts it into the dictionary with the given value (here [])
    # and then returns that default.
    messages.setdefault(thread, [])

    counters = metadata.setdefault("message_id_counters", {})
    next_id = counters.get(thread, 0)
    counters[thread] = next_id + 1

    messages[thread].append({"author": author, "content": content, "id": next_id})

    # write both files (order doesn't matter because both are atomic)
    save_all_messages(messages)
    save_metadata(metadata)
    return next_id


def delete_message(thread: Optional[str], message_id: int) -> bool:
    """
    Delete message by id in the given thread. Return True if something was deleted.
    """
    if thread is None:
        thread = get_current_thread()
    if thread is None:
        return False
    messages = load_messages()
    if thread not in messages:
        return False
    before = len(messages[thread])
    messages[thread] = [m for m in messages[thread] if m.get("id") != message_id]
    after = len(messages[thread])
    if before == after:
        return False
    save_all_messages(messages)
    return True


def start_thread(thread_name: str) -> bool:
    """
    Create a new thread. Return False if thread already existed, True if created.
    """
    messages = load_messages()
    if thread_name in messages:
        return False
    messages[thread_name] = []
    save_all_messages(messages)
    metadata = load_metadata()
    metadata.setdefault("message_id_counters", {})[thread_name] = 0
    save_metadata(metadata)
    return True






# ----------------------------------------------------------------------------
#                                OLD FUNCTIONS
# ----------------------------------------------------------------------------
def get_current_thread_old():
    try:
        with open(METADATA_FILE, 'r') as f:
            metadata = json.load(f)
            return metadata['current_thread']
    except (FileNotFoundError, json.JSONDecodeError):
        return None

    
def save_user_old(username, password):
    users = load_users()
    if username in users:
        return False    # User already exists.
    users[username] = {}
    users[username]['password'] = password
    users[username]['admin'] = 0
    with open(USER_FILE, 'w') as f:
        json.dump(users, f)
    return True

def verify_user_old(username, password):
    users = load_users()
    if username not in users:
        return False
    if users[username]["password"] == password:
        return True
    else:
        return False

def load_messages_old():
    try:
        with open(MESSAGE_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    
def load_messages_thread_old():
    try:
        all_messages = load_messages()
        with open(METADATA_FILE, 'r') as f:
            metadata = json.load(f)
        thread = metadata['current_thread']
        messages = all_messages[thread]
        return messages
    
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    
def load_threads_old():
    threads = load_messages().keys()
    return threads

def save_message_old(name, content):
    with open(METADATA_FILE, 'r') as f:
        metadata = json.load(f)
    thread = metadata['current_thread']
    message_id = metadata["message_id_counters"][thread]
    metadata["message_id_counters"][thread] += 1

    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f)

    messages = load_messages()
    messages[thread].append({'author': name, 'content': content, 'id': message_id})
    with open(MESSAGE_FILE, 'w') as f:
        json.dump(messages, f)

def save_all_messages_old(messages):
    with open(MESSAGE_FILE, 'w') as f:
        json.dump(messages, f)

def delete_message_old(message_id):
    thread = get_current_thread()
    messages = load_messages()
    new_messages_thread = [msg for msg in messages[thread] if msg["id"] != message_id]
    messages[thread] = new_messages_thread
    save_all_messages(messages)

def start_thread_old(content):
    # Add message id counter to metadata file for new thread
    with open(METADATA_FILE, 'r') as f:
        metadata = json.load(f)
    metadata["message_id_counters"][content] = 0
    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f)

    # Add list for messages of new thread to message file
    messages = load_messages()
    messages[content] = []
    save_all_messages(messages)

def change_thread_old(new_thread):
    print("Changing thread")
    with open(METADATA_FILE, 'r') as f:
        metadata = json.load(f)
    metadata["current_thread"] = new_thread
    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f)