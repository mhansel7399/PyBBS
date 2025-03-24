import message_base_manager

def main_menu(client_socket, recv_line):
    """Displays and handles the main menu."""
    while True:
        menu = """
Main Menu:
1. Message Boards
2. Exit
Choose an option: """
        client_socket.send(menu.encode('utf-8'))
        choice = recv_line(client_socket)

        if choice == '1':
            # Redirect to the message board menu
            message_base_manager.message_board_menu(client_socket, recv_line)
        elif choice == '2':
            client_socket.send(b"Goodbye! Disconnecting...\r\n")
            client_socket.close()  # Gracefully close the connection
            break
        else:
            client_socket.send(b"Invalid option. Please try again.\r\n")