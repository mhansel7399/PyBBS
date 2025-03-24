import message_base_manager

async def main_menu(reader, writer, recv_line):
    """Displays and handles the main menu."""
    while True:
        menu = """
Main Menu:
1. Message Boards
2. Exit
Choose an option: """
        writer.write(menu)
        await writer.drain()
        choice = await recv_line()

        if choice == '1':
            # Redirect to the message board menu
            await message_base_manager.message_board_menu(reader, writer, recv_line)
        elif choice == '2':
            writer.write("Goodbye! Disconnecting...\r\n")
            await writer.drain()
            writer.close()
            break
        else:
            writer.write("Invalid option. Please try again.\r\n")
            await writer.drain()