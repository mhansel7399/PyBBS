import json
from textwrap import wrap
from datetime import datetime

def write_message(reader, writer, recv_line):
    """Handles writing a multi-line message."""
    writer.write("Enter your message (Press Enter for a new line, type '.' on a new line to finish):\r\n")
    message_content = ""
    while True:
        line = await recv_line()
        if line.strip() == ".":  # User signals end of message with "."
            break
        message_content += line + "\n"  # Append newline character
    return message_content.strip()

def wrap_message(content, width=80):
    """Wraps a message to the specified width."""
    return "\n".join(wrap(content, width))

async def save_message(board_name, content, data_dir="bbs_data"):
    """Saves the message to the specified board."""
    import os

    board_path = os.path.join(data_dir, board_name)
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