import socket
import threading
import user_management

# Flag to control the server loop
running = True

def start_telnet_server(host='172.16.26.220', port=23):
    global running
    welcome_message = """
\033[1;32mWelcome to the Python BBS!\033[0m\r
\033[1;34m--------------------------\033[0m\r
\033[1;37mPlease enter your commands below:\033[0m\r
"""

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Telnet server started on {host}:{port}")

    def stop_server():
        global running
        input("Press Enter to stop the server...\n")
        running = False
        server_socket.close()

    # Start a thread to listen for the stop command
    threading.Thread(target=stop_server, daemon=True).start()

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

    while running:
        try:
            client_socket, client_address = server_socket.accept()
            print(f"Connection from {client_address}")
            client_socket.send(welcome_message.encode('utf-8'))

            # Prompt for registration or login
            client_socket.send(b"Do you want to (1) Register or (2) Login? ")
            choice = recv_line(client_socket)
            client_socket.send(f"\r\nYou selected: {choice}\r\n".encode('utf-8'))

            if choice == '1':
                client_socket.send(b"Enter a new username: ")
                username = recv_line(client_socket)
                ## client_socket.send(f"\r\nUsername: {username}\r\n".encode('utf-8'))
                client_socket.send(b"\r\n")

                client_socket.send(b"Enter a new password: ")
                password = recv_line(client_socket, mask_input=True)
                client_socket.send(b"\r\n")

                if not username:
                    client_socket.send(b"Username cannot be empty. Connection closed.\r\n")
                    client_socket.close()
                    continue

                if not password:
                    client_socket.send(b"Password cannot be empty. Connection closed.\r\n")
                    client_socket.close()
                    continue

                if user_management.add_user(username, password):
                    client_socket.send(b"Registration successful!\r\n")
                else:
                    client_socket.send(b"Username already exists. Connection closed.\r\n")
                    client_socket.close()
                    continue
            elif choice == '2':
                client_socket.send(b"Username: ")
                username = recv_line(client_socket)
                ## client_socket.send(f"\r\nUsername: {username}\r\n".encode('utf-8'))
                client_socket.send(b"\r\n")
                client_socket.send(b"Password: ")
                password = recv_line(client_socket, mask_input=True)
                client_socket.send(b"\r\n")

                if not username:
                    client_socket.send(b"Username cannot be empty. Connection closed.\r\n")
                    client_socket.close()
                    continue

                if not password:
                    client_socket.send(b"Password cannot be empty. Connection closed.\r\n")
                    client_socket.close()
                    continue

                if user_management.authenticate(username, password):
                    client_socket.send(b"Login successful!\r\n")
                else:
                    client_socket.send(b"Invalid credentials. Connection closed.\r\n")
                    client_socket.close()
                    continue
            else:
                client_socket.send(b"Invalid choice. Connection closed.\r\n")
                client_socket.close()
                continue
            
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                client_socket.send(data)
            
            client_socket.close()
            print(f"Connection closed from {client_address}")
        except OSError:
            break
        
    print("Server stopped.")

if __name__ == "__main__":
    start_telnet_server()