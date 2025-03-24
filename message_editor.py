import json
from datetime import datetime
import os
from textwrap import wrap

DATA_DIR = "bbs_data"
os.makedirs(DATA_DIR, exist_ok=True)

async def write_message(reader, writer, recv_line, wrap_width=79):
    """Handles writing a multi-line message with live word wrapping and accurate end signal detection."""
    writer.write("Enter your message (Type '.' on a new line to finish):\r\n")
    await writer.drain()

    message_content = []  # Stores completed lines of the message
    current_line = []     # Stores characters for the current line
    word_buffer = []      # Temporary storage for the current word
    line_length = 0       # Tracks the current line's character count

    while True:
        char = await reader.read(1)  # Read one character from the client
        if not char:  # Handle disconnection
            return None

        if char in ('\n', '\r'):  # User presses Enter
            # Join the current word buffer and line to form the full current line
            full_line = ''.join(current_line + word_buffer).strip()
            if full_line == ".":  # Detect only a single period as the end signal
                break
            message_content.append(full_line)  # Add the completed line to the message
            writer.write("\r\n")  # Move to the next line visually
            await writer.drain()
            current_line = []  # Reset the current line
            word_buffer = []   # Reset the word buffer
            line_length = 0    # Reset the line length counter

        elif char == '\x08':  # Backspace character
            if word_buffer:  # Remove from the current word first
                word_buffer.pop()
            elif current_line:  # Then remove from the current line
                current_line.pop()
                line_length -= 1
            writer.write("\b \b")  # Visual feedback for backspace
            await writer.drain()

        else:
            if char == ' ':  # Handle spaces
                # Add the current word buffer to the line
                current_line.extend(word_buffer)
                current_line.append(char)  # Add the space
                word_buffer = []  # Reset the buffer
                line_length = len(''.join(current_line))
            else:
                word_buffer.append(char)  # Add character to the word buffer

            # Check if the line length exceeds the adjusted wrap width
            if line_length + len(''.join(word_buffer)) >= wrap_width:
                # Finalize the current line and move the word buffer to the next line
                current_line.extend(word_buffer)  # Ensure word buffer is part of the current line
                message_content.append(''.join(current_line).strip())  # Complete the line
                writer.write("\r\n")  # Move visually to the next line
                await writer.drain()
                current_line = word_buffer[:]  # Start the new line with the word buffer
                word_buffer = []  # Reset the word buffer
                line_length = len(''.join(current_line))  # Update line length with carried-over word

            # Echo characters back as they are typed
            writer.write(char)
            await writer.drain()

    # Add any remaining content in the buffers to the final message
    if word_buffer:
        current_line.extend(word_buffer)
    if current_line:
        message_content.append(''.join(current_line).strip())

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