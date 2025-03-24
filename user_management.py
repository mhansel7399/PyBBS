def handle_user_authentication_flow(client_socket, recv_line):
    """Handles the user authentication flow (welcome, register, or login)."""
    try:
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
    except Exception as e:
        # Log the error and notify the client
        print(f"Error in authentication flow: {e}")
        client_socket.send(b"An error occurred during authentication. Connection closed.\r\n")
        return False

def handle_registration(client_socket, recv_line):
    """Handles user registration via the telnet server."""
    try:
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
    except Exception as e:
        print(f"Error in registration: {e}")
        client_socket.send(b"An error occurred during registration. Connection closed.\r\n")
        return False

def handle_authentication(client_socket, recv_line):
    """Handles user authentication via the telnet server."""
    try:
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
    except Exception as e:
        print(f"Error in authentication: {e}")
        client_socket.send(b"An error occurred during authentication. Connection closed.\r\n")
        return False