import json
from textwrap import wrap
from datetime import datetime
import os

DATA_DIR = "bbs_data"
os.makedirs(DATA_DIR, exist_ok=True)

async def write_message(reader, writer, recv_line, wrap_width=80):
    """Handles writing a multi-line message with real-time word wrapping and newline visibility."""
    writer.write("Enter your message (Press Enter for a new line, type '.' on a new line to finish):\r\n")
    await writer.drain()

    message_content = ""
    current_line = ""
    while True:
        char = await reader.read(1)
        if not char:  # Handle disconnection
            return None

        if char in ('\n', '\r'):  # End of line
            if current_line.strip() == ".":  # User signals end of message
                break
            message_content += current_line.strip() + "\n"
            writer.write("\r\n")  # Move to the next line visually
            await writer.drain()
            current_line = ""
        elif char == '\x08':  # Backspace
            if current_line:
                current_line = current_line[:-1]  # Remove last character
                writer.write("\b \b")  # Visual backspace
                await writer.drain()
        else:
            current_line += char
            if len(current_line) > wrap_width:  # Handle word wrapping
                message_content += current_line.strip() + "\n"
                writer.write("\r\n")  # Move to the next line visually
                await writer.drain()
                current_line = ""  # Reset the current line
            else:
                writer.write(char)  # Echo the character to the client
                await writer.drain()

    return message_content.strip()

def wrap_message(content, width=80):
    """Wraps a message to the specified width."""
    return "\n".join(wrap(content, width))

async def save_message(board_name, content):
    """Saves the message to the specified board."""
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