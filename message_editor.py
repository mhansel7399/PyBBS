import os
import json
from datetime import datetime

DATA_DIR = "bbs_data"
os.makedirs(DATA_DIR, exist_ok=True)

def save_message(board_name, content):
    board_path = os.path.join(DATA_DIR, board_name)
    os.makedirs(board_path, exist_ok=True)

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