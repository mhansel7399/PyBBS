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
    """Checks if the username and password match."""
    users = load_users()
    return username in users and users[username] == password

def add_user(username, password):
    """Adds a new user to the system."""
    users = load_users()
    if username in users:
        return False  # User already exists
    users[username] = password
    save_users(users)
    return True

async def handle_registration(reader, writer, recv_line):
    """Handles user registration via the telnet server."""
    writer.write("Enter a new username: ")
    await writer.drain()
    username = await recv_line()

    writer.write("\r\nEnter a new password: ")
    await writer.drain()
    password = await recv_line(mask_input=True)

    if not username or not password:
        writer.write("\r\nUsername or password cannot be empty. Connection closed.\r\n")
        await writer.drain()
        return False

    if add_user(username, password):
        writer.write("\r\nRegistration successful!\r\n")
        await writer.drain()
        return True
    else:
        writer.write("\r\nUsername already exists. Connection closed.\r\n")
        await writer.drain()
        return False

async def handle_authentication(reader, writer, recv_line):
    """Handles user authentication via the telnet server."""
    writer.write("Username: ")
    await writer.drain()
    username = await recv_line()

    writer.write("\r\nPassword: ")
    await writer.drain()
    password = await recv_line(mask_input=True)

    if not username or not password:
        writer.write("\r\nUsername or password cannot be empty. Connection closed.\r\n")
        await writer.drain()
        return False

    # Call the `authenticate` function here
    if authenticate(username, password):
        writer.write("\r\nLogin successful!\r\n")
        await writer.drain()
        return True
    else:
        writer.write("\r\nInvalid credentials. Connection closed.\r\n")
        await writer.drain()
        return False

async def handle_user_authentication_flow(reader, writer, recv_line):
    """Handles the user authentication flow (welcome, register, or login)."""
    writer.write("Welcome to the Python BBS!\r\n")
    writer.write("Do you want to (1) Register or (2) Login? ")
    await writer.drain()
    choice = await recv_line()

    if choice == '1':  # Registration
        return await handle_registration(reader, writer, recv_line)
    elif choice == '2':  # Login
        return await handle_authentication(reader, writer, recv_line)
    else:
        writer.write("Invalid choice. Connection closed.\r\n")
        await writer.drain()
        return False