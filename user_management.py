import json

USER_FILE = 'users.json'

def handle_user_authentication_flow(client_socket, recv_line):
    """Handles the user authentication flow (welcome, register, or login)."""
    client_socket.send(b"Welcome to the Python BBS!\r\n")
    client_socket.send(b"Do you want to (1) Register or (2) Login? ")
    choice = recv_line(client_socket)

    if choice == '1':  # Registration
        return handle_registration(client_socket, recv_line)
    elif choice == '2':  # Login
        return handle_authentication(client_socket, recv_line)
    else:
        client_socket.send(b"Invalid choice. Connection closed.\r\n")
        return False

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