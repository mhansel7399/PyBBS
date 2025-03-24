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
        print(f"Error in authentication flow: {e}")
        client_socket.send(b"An error occurred during authentication. Connection closed.\r\n")
        return False