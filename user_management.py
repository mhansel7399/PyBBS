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

def handle_registration(client_socket, recv_line):
    """Handles user registration via the telnet server."""
    client_socket.send(b"Enter a new username: ")
    username = recv_line(client_socket)
    client_socket.send(b"\r\nEnter a new password: ")
    password = recv_line(client_socket, mask_input=True)

    if not username or not password:
        client_socket.send(b"\r\nUsername or password cannot be empty. Connection closed.\r\n")
        return False

    if add_user(username, password):
        client_socket.send(b"\r\nRegistration successful!\r\n")
        return True
    else:
        client_socket.send(b"\r\nUsername already exists. Connection closed.\r\n")
        return False

def handle_authentication(client_socket, recv_line):
    """Handles user authentication via the telnet server."""
    client_socket.send(b"Username: ")
    username = recv_line(client_socket)
    client_socket.send(b"\r\nPassword: ")
    password = recv_line(client_socket, mask_input=True)

    if not username or not password:
        client_socket.send(b"\r\nUsername or password cannot be empty. Connection closed.\r\n")
        return False

    if authenticate(username, password):
        client_socket.send(b"\r\nLogin successful!\r\n")
        return True
    else:
        client_socket.send(b"\r\nInvalid credentials. Connection closed.\r\n")
        return False

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