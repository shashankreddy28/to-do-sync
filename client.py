import asyncio
from logging_setup import setup_logging

HOST = "127.0.0.1"
PORT = 5055
TIMEOUT = 5

# Initialize logger
logger = setup_logging('client')


async def async_input(prompt):
    return await asyncio.to_thread(input, prompt)


async def receive_messages(reader):
    while True:
        try:
            data = await reader.readline()
            if not data:
                print("\n[Disconnected from server]")
                logger.warning("Disconnected from server")
                break

            message = data.decode().strip()

            if message.startswith("LIST"):
                print("\n--- Tasks ---")
                tasks = message.replace("LIST", "").strip()

                if not tasks:
                    print("No tasks found.")
                else:
                    for task in tasks.split(";"):
                        print(task.strip())

            elif message.startswith("UPDATE"):
                print(f"\n[Server Update] {message}")
                logger.info(f"Received update from server: {message}")

            elif message.startswith("OK"):
                print(f"[Success] {message}")
                logger.info(f"Received success message from server: {message}")

            elif message.startswith("ERROR"):
                print(f"[Error] {message}")
                logger.error(f"Received error message from server: {message}")

            else:
                print(f"[Server] {message}")
                logger.info(f"Received unknown message from server: {message}")

        except ConnectionResetError:
            print("\n[Error] Server disconnected unexpectedly.")
            logger.error("Server disconnected unexpectedly.")
            break


async def send_commands(writer):
    while True:
        print("\n1. Add task")
        print("2. View tasks")
        print("3. Delete task")
        print("4. Exit")

        choice = (await async_input("Choose an option: ")).strip()

        if choice == "1":
            text = (await async_input("Enter task: ")).strip()
            if text:
                command = f"ADD {text}\r\n"
            else:
                print("[Error] Task cannot be empty.")
                logger.warning("Attempted to add empty task.")
                continue

        elif choice == "2":
            command = "VIEW\r\n"
            logger.info("Requested task list from server.")

        elif choice == "3":
            task_id = (await async_input("Enter task ID: ")).strip()
            command = f"DELETE {task_id}\r\n"
            logger.info(f"Attempted to delete task ID: {task_id}")

        elif choice == "4":
            print("Closing client.")
            writer.close()
            await writer.wait_closed()
            break

        else:
            print("[Error] Invalid menu option.")
            continue

        writer.write(command.encode())
        await writer.drain()


async def main():
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(HOST, PORT),
            timeout=TIMEOUT
        )

        print(f"Connected to server at {HOST}:{PORT}")
        logger.info(f"Connected to server at {HOST}:{PORT}")

        receive_task = asyncio.create_task(receive_messages(reader))
        logger.info("Ready to receive messages from server.")
        send_task = asyncio.create_task(send_commands(writer))
        logger.info("Ready to send commands to server.")

        await asyncio.gather(receive_task, send_task)

    except ConnectionRefusedError:
        print("[Error] Could not connect. Server may be down or IP/port is wrong.")
        logger.error("Connection refused. Server may be down or IP/port is wrong.")

    except asyncio.TimeoutError:
        print("[Error] Connection timed out.")
        logger.error("Connection timed out.")

    except ConnectionResetError:
        print("[Error] Server reset the connection.")
        logger.error("Server reset the connection.")

    except KeyboardInterrupt:
        print("\nClient stopped.")
        logger.info("Client stopped by user.")

if __name__ == "__main__":
    asyncio.run(main())
