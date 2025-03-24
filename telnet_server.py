import socket
import threading
import user_management
import message_base_manager  # Import the new module

# Global flag to control server loop
running = True

def handle_client(client_socket):
    def recv_line(sock, mask_input=False):
        line = ""
        while True:
            char = sock.recv(1).decode('utf-8')
            if char in ('\n', '\r'):
                break
            if mask_input:
                sock.send(b'#')
            else:
                sock.send(char.encode('utf-8'))
            line += char
        return line.strip()

    # Authentication/Registration
    client_socket.send(b"Welcome to the Python BBS!\r\n")
    client_socket.send(b"Do you want to (1) Register or (2) Login? ")
    choice = recv_line(client_socket)

    if choice == '1':
        client_socket.send(b"Enter a new username: ")
        username = recv_line(client_socket)
        client_socket.send(b"\r\nEnter a new password: ")
        password = recv_line(client_socket, mask_input=True)
        if user_management.add_user(username, password):
            client_socket.send(b"\r\nRegistration successful!\r\n")
        else:
            client_socket.send(b"\r\nUsername already exists. Connection closed.\r\n")
            client_socket.close()
            return
    elif choice == '2':
        client_socket.send(b"Username: ")
        username = recv_line(client_socket)
        client_socket.send(b"\r\nPassword: ")
        password = recv_line(client_socket, mask_input=True)
        if not user_management.authenticate(username, password):
            client_socket.send(b"\r\nInvalid credentials. Connection closed.\r\n")
            client_socket.close()
            return
        client_socket.send(b"\r\nLogin successful!\r\n")
    else:
        client_socket.send(b"Invalid choice. Connection closed.\r\n")
        client_socket.close()
        return

    # Main menu
    while True:
        menu = """
Main Menu:
1. List message boards
2. Create a new message board
3. Post a new message
4. View messages
5. Exit
Choose an option: """
        client_socket.send(menu.encode('utf-8'))
        choice = recv_line(client_socket)

        if choice == '1':
            boards = message_base_manager.list_boards()
            if boards:
                client_socket.send(b"Available message boards:\r\n")
                for board in boards:
                    client_socket.send(f"- {board}\r\n".encode('utf-8'))
            else:
                client_socket.send(b"No message boards found.\r\n")
        elif choice == '2':
            client_socket.send(b"Enter the name of the new board: ")
            board_name = recv_line(client_socket)
            result = message_base_manager.create_board(board_name)
            client_socket.send(f"{result}\r\n".encode('utf-8'))
        elif choice == '3':
            client_socket.send(b"Enter the board name: ")
            board_name = recv_line(client_socket)
            client_socket.send(b"Enter your message: ")
            content = recv_line(client_socket)
            result = message_base_manager.save_message(board_name, content)
            client_socket.send(f"{result}\r\n".encode('utf-8'))
        elif choice == '4':
            client_socket.send(b"Enter the board name: ")
            board_name = recv_line(client_socket)
            messages = message_base_manager.load_messages(board_name)
            if not messages:
                client_socket.send(b"No messages found.\r\n")
            else:
                for msg in messages:
                    client_socket.send(f"ID: {msg['id']} | {msg['timestamp']}\r\n{msg['content']}\r\n{'-'*40}\r\n".encode('utf-8'))
        elif choice == '5':
            client_socket.send(b"Goodbye!\r\n")
            break
        else:
            client_socket.send(b"Invalid option. Please try again.\r\n")

    client_socket.close()

def start_telnet_server(host='0.0.0.0', port=23):
    global running
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Telnet server started on {host}:{port}")

    def stop_server():
        global running
        input("Press Enter to stop the server...\n")
        running = False
        server_socket.close()

    threading.Thread(target=stop_server, daemon=True).start()

    while running:
        try:
            client_socket, client_address = server_socket.accept()
            print(f"Connection from {client_address}")
            threading.Thread(target=handle_client, args=(client_socket,)).start()
        except OSError:
            break
    print("Server stopped.")

if __name__ == "__main__":
    start_telnet_server()