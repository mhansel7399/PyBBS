import json

USER_FILE = 'users.json'

def load_users():
    try:
        with open(USER_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_users(users):
    with open(USER_FILE, 'w') as file:
        json.dump(users, file, indent=4)

def authenticate(username, password):
    users = load_users()
    return username in users and users[username] == password

def add_user(username, password):
    users = load_users()
    if username in users:
        return False  # User already exists
    users[username] = password
    save_users(users)
    return True