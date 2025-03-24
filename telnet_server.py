import telnetlib3
import asyncio
import user_management
import menu

async def handle_client(reader, writer):
    """Handles client communication and delegates tasks to appropriate modules."""
    async def recv_line(mask_input=False):
        """Receives a line of input from the client and provides real-time feedback."""
        line = ""
        while True:
            char = await reader.read(1)
            if not char:  # Client disconnected
                return None
            if char in ('\n', '\r'):  # End of input
                break
            if char == '\x08':  # Backspace character
                if line:  # Only process backspace if there's something to delete
                    line = line[:-1]  # Remove the last character from the input
                    writer.write('\b \b')  # Send backspace visual update to client
                    await writer.drain()
            elif mask_input:
                writer.write('#')  # Mask input for passwords
                await writer.drain()
                line += char
            else:
                writer.write(char)  # Echo the character back to the client
                await writer.drain()
                line += char
        return line.strip()

    try:
        # Send initial welcome message
        writer.write("Welcome to the Python BBS!\r\n")
        await writer.drain()

        # Delegate user authentication flow
        authenticated = await user_management.handle_user_authentication_flow(reader, writer, recv_line)
        if not authenticated:
            writer.write("Connection closed.\r\n")
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            return

        # Redirect to main menu after successful authentication
        await menu.main_menu(reader, writer, recv_line)

    except Exception as e:
        # Log the error and notify the client
        print(f"Error handling client: {e}")
        writer.write("An error occurred. Connection closed.\r\n")
        await writer.drain()
        writer.close()
        await writer.wait_closed()

async def start_telnet_server(host='0.0.0.0', port=23):
    """Starts the Telnet server using telnetlib3."""
    await telnetlib3.create_server(port=port, host=host, shell=handle_client)
    print(f"Telnet server started on {host}:{port} using telnetlib3.")
    try:
        await asyncio.Future()  # Run forever
    except KeyboardInterrupt:
        print("Server stopped.")

if __name__ == "__main__":
    asyncio.run(start_telnet_server())