import asyncio

HOST = "127.0.0.1"
PORT = 5055
TIMEOUT = 5


async def receive_messages(reader):
    while True:
        try:
            data = await reader.readline()
            if not data:
                print("\n[Disconnected from server]")
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

            elif message.startswith("OK"):
                print(f"[Success] {message}")

            elif message.startswith("ERROR"):
                print(f"[Error] {message}")

            else:
                print(f"[Server] {message}")

        except ConnectionResetError:
            print("\n[Error] Server disconnected unexpectedly.")
            break


async def send_commands(writer):
    while True:
        print("\n1. Add task")
        print("2. View tasks")
        print("3. Delete task")
        print("4. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            text = input("Enter task: ").strip()
            if text:
                command = f"ADD {text}\r\n"
            else:
                print("[Error] Task cannot be empty.")
                continue

        elif choice == "2":
            command = "VIEW\r\n"

        elif choice == "3":
            task_id = input("Enter task ID: ").strip()
            command = f"DELETE {task_id}\r\n"

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

        receive_task = asyncio.create_task(receive_messages(reader))
        send_task = asyncio.create_task(send_commands(writer))

        await asyncio.gather(receive_task, send_task)

    except ConnectionRefusedError:
        print("[Error] Could not connect. Server may be down or IP/port is wrong.")

    except asyncio.TimeoutError:
        print("[Error] Connection timed out.")

    except ConnectionResetError:
        print("[Error] Server reset the connection.")

    except KeyboardInterrupt:
        print("\nClient stopped.")


if __name__ == "__main__":
    asyncio.run(main())
