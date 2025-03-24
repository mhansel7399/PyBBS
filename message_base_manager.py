import os
import json
import re
from datetime import datetime

DATA_DIR = "bbs_data"
os.makedirs(DATA_DIR, exist_ok=True)

def list_boards():
    """Lists all available message boards."""
    return [board for board in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, board))]

def create_board(board_name):
    """Creates a new message board if it doesn't already exist."""
    # Sanitize board_name by removing invalid characters
    board_name = re.sub(r'[<>:"/\\|?*\x08]', '', board_name)  # Remove invalid characters

    if not board_name.strip():
        return "Invalid board name. Please use a valid name."

    board_path = os.path.join(DATA_DIR, board_name)
    if not os.path.exists(board_path):
        os.makedirs(board_path)
        return f"Board '{board_name}' created successfully."
    return f"Board '{board_name}' already exists."

def save_message(board_name, content):
    """Saves a message to the specified board."""
    board_path = os.path.join(DATA_DIR, board_name)
    if not os.path.exists(board_path):
        return f"Board '{board_name}' does not exist."

    metadata_file = os.path.join(board_path, "metadata.json")
    if os.path.exists(metadata_file):
        with open(metadata_file, "r") as f:
            board_metadata = json.load(f)
    else:
        board_metadata = {"messages": []}

    message_id = len(board_metadata["messages"]) + 1
    timestamp = datetime.now().isoformat()
    message_file = f"message_{message_id}.json"
    message_data = {"id": message_id, "timestamp": timestamp, "content": content}

    with open(os.path.join(board_path, message_file), "w") as f:
        json.dump(message_data, f, indent=4)

    board_metadata["messages"].append({"id": message_id, "file": message_file})
    with open(metadata_file, "w") as f:
        json.dump(board_metadata, f, indent=4)

    return f"Message {message_id} saved to board '{board_name}'."

def load_messages(board_name):
    """Loads all messages from the specified board."""
    board_path = os.path.join(DATA_DIR, board_name)
    metadata_file = os.path.join(board_path, "metadata.json")

    if not os.path.exists(metadata_file):
        return []

    with open(metadata_file, "r") as f:
        board_metadata = json.load(f)

    messages = []
    for message_info in board_metadata["messages"]:
        with open(os.path.join(board_path, message_info["file"]), "r") as f:
            messages.append(json.load(f))

    return messages

async def message_board_menu(reader, writer, recv_line):
    """Displays and handles the message board menu."""
    while True:
        menu = """
Message Board Menu:
1. List message boards
2. Create a new message board
3. Post a new message
4. View messages
5. Return to main menu
Choose an option: """
        writer.write(menu)
        await writer.drain()
        choice = await recv_line()

        if choice == '1':
            boards = list_boards()
            if boards:
                writer.write("Available message boards:\r\n")
                for board in boards:
                    writer.write(f"- {board}\r\n")
                await writer.drain()
            else:
                writer.write("No message boards found.\r\n")
                await writer.drain()
        elif choice == '2':
            writer.write("Enter the name of the new board: ")
            await writer.drain()
            board_name = await recv_line()
            result = create_board(board_name)
            writer.write(f"{result}\r\n")
            await writer.drain()
        elif choice == '3':
            writer.write("Enter the board name: ")
            await writer.drain()
            board_name = await recv_line()
            writer.write("Enter your message: ")
            await writer.drain()
            content = await recv_line()
            result = save_message(board_name, content)
            writer.write(f"{result}\r\n")
            await writer.drain()
        elif choice == '4':
            writer.write("Enter the board name: ")
            await writer.drain()
            board_name = await recv_line()
            messages = load_messages(board_name)
            if not messages:
                writer.write("No messages found.\r\n")
                await writer.drain()
            else:
                for msg in messages:
                    writer.write(f"ID: {msg['id']} | {msg['timestamp']}\r\n{msg['content']}\r\n{'-'*40}\r\n")
                    await writer.drain()
        elif choice == '5':
            return  # Return to the main menu
        else:
            writer.write("Invalid option. Please try again.\r\n")
            await writer.drain()