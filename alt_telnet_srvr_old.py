## telnet server using telnetlib3 and aysncio
## this is not being used currently
import asyncio
import telnetlib3

async def shell(reader, writer):
    welcome_message = """
\033[1;32mWelcome to the Python BBS!\033[0m\033[1;34m--------------------------\033[0m\033[1;37mPlease enter your commands below:\033[0m"""
    welcome_message_title = "\033[1;32mWelcome to the Python BBS!\033[0m\r\n"
    welcome_message_divider = "\033[1;34m--------------------------\033[0m\r\n"
    welcome_message_instruct = "\033[1;37mPlease enter your commands below:\033[0m\r\n"
    ##writer.write(welcome_message)
    writer.write(welcome_message_title)
    writer.write(welcome_message_divider)
    writer.write(welcome_message_instruct)
    await writer.drain()

    while True:
        data = await reader.read(1024)
        if not data:
            break
        writer.write(data)
        await writer.drain()

    writer.close()
    await writer.wait_closed()

async def main():
    server = await telnetlib3.create_server(port=23, shell=shell)
    await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
