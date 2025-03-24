import json
from textwrap import wrap
from datetime import datetime
import os

DATA_DIR = "bbs_data"
os.makedirs(DATA_DIR, exist_ok=True)

async def write_message(reader, writer, recv_line, wrap_width=78):
    """Handles writing a multi-line message with live word wrapping."""
    writer.write("Enter your message (Type '.' on a new line to finish):\r\n")
    await writer.drain()

    message_content = []
    current_line = []
    line_length = 0

    while True:
        char = await reader.read(1)
        if not char:  # Handle disconnection
            return None

        if char in ('\n', '\r'):  # Newline character
            if ''.join(current_line).strip() == ".":  # End of message
                break
            message_content.append(''.join(current_line).strip())  # Append the current line
            writer.write("\r\n")  # Move to the next line visually
            await writer.drain()
            current_line = []
            line_length = 0

        elif char == '\x08':  # Backspace character
            if current_line:
                current_line.pop()  # Remove the last character
                line_length -= 1
                writer.write("\b \b")  # Visual backspace
                await writer.drain()

        else:
            current_line.append(char)
            line_length += 1
            writer.write(char)  # Echo character to client
            await writer.drain()

            if line_length >= wrap_width:  # Check for word wrap
                # Find the last space in the current line
                last_space_index = ''.join(current_line).rfind(' ')
                if last_space_index != -1:
                    # Wrap at the last space
                    message_content.append(''.join(current_line[:last_space_index]).strip())
                    writer.write("\r\n")  # Move to the next line visually
                    await writer.drain()
                    # Carry over remaining characters after the space
                    current_line = current_line[last_space_index + 1:]
                    line_length = len(''.join(current_line))  # Update line length
                else:
                    # No space found, force wrap
                    message_content.append(''.join(current_line).strip())
                    writer.write("\r\n")
                    await writer.drain()
                    current_line = []
                    line_length = 0

    # Join all lines into the final message
    return '\n'.join(message_content).strip()

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