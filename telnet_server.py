import socket
import threading
import user_management
import menu

running = True

def handle_client(client_socket):
    """Handles client communication and delegates tasks to appropriate modules."""
    def recv_line(sock, mask_input=False):
        """Receives a line of input from the client and provides visual feedback for edits."""
        line = ""
        while True:
            char = sock.recv(1).decode('utf-8')
            if char in ('\n', '\r'):  # End of input
                break
            if char == '\x08':  # Backspace character
                if line:  # Only process backspace if there's something to delete
                    line = line[:-1]  # Remove the last character from the input
                    sock.send(b'\b \b')  # Send backspace with visual feedback (erase character and move back)
            elif mask_input:
                sock.send(b'#')  # Mask input for passwords
                line += char
            else:
                sock.send(char.encode('utf-8'))  # Echo the character back to the client
                line += char
        return line.strip()
    try:
        # Delegate user authentication flow
        authenticated = user_management.handle_user_authentication_flow(client_socket, recv_line)
        if not authenticated:
            client_socket.send(b"Connection closed.\r\n")
            client_socket.close()
            return

        # Redirect to main menu after successful authentication
        menu.main_menu(client_socket, recv_line)
    except Exception as e:
        # Log the error and notify the client
        print(f"Error handling client: {e}")
        client_socket.send(b"An error occurred. Connection closed.\r\n")
        client_socket.close()

def start_telnet_server(host='0.0.0.0', port=23):
    """Starts the Telnet server."""
    global running
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Telnet server started on {host}:{port}")

    def stop_server():
        """Stops the server gracefully."""
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