import socket
import threading
import message_editor
import user_management

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

    # Welcome and authentication
    client_socket.send(b"Welcome to the Python BBS!\r\n")
    client_socket.send(b"Do you want to (1) Register or (2) Login? ")
    choice = recv_line(client_socket)

    if choice == '1':
        client_socket.send(b"\r\nEnter a new username: ")
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
        client_socket.send(b"\r\nUsername: ")
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
\r\nMain Menu:
\r\n1. Post a new message
\r\n2. View messages
\r\n3. Exit
\r\nChoose an option: """
        client_socket.send(menu.encode('utf-8'))
        choice = recv_line(client_socket)

        if choice == '1':
            client_socket.send(b"\r\nEnter the board name: ")
            board_name = recv_line(client_socket)
            client_socket.send(b"\r\nEnter your message: ")
            content = recv_line(client_socket)
            result = message_editor.save_message(board_name, content)
            client_socket.send(f"{result}\r\n".encode('utf-8'))
        elif choice == '2':
            client_socket.send(b"\r\nEnter the board name: ")
            board_name = recv_line(client_socket)
            messages = message_editor.load_messages(board_name)
            if not messages:
                client_socket.send(b"\r\nNo messages found.\r\n")
            else:
                for msg in messages:
                    client_socket.send(f"ID: {msg['id']} | {msg['timestamp']}\r\n{msg['content']}\r\n{'-'*40}\r\n".encode('utf-8'))
        elif choice == '3':
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