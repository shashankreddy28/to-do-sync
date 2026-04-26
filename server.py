import asyncio

# Global state
tasks = {}
task_id_counter = 1 # Acts as our unique primary key generator

def parse_command(message, peername):
    global task_id_counter
    
    # Strip whitespace and split the message into components
    parts = message.strip().split(" ", 1)
    command = parts[0].upper()

    if command == "ADD" and len(parts) > 1:
        text = parts[1]
        task_id = task_id_counter
        tasks[task_id] = {"text": text, "owner": peername}
        task_id_counter += 1
        return f"OK Task added ID={task_id}\n"

    elif command == "VIEW":
        if not tasks:
            return "LIST EMPTY\n"
        response = "LIST\n"
        for t_id, task in tasks.items():
            response += f"{t_id}: {task['text']} (from {task['owner']})\n"
        return response

    elif command == "DELETE" and len(parts) > 1:
        try:
            task_id = int(parts[1])
            if task_id in tasks:
                del tasks[task_id]
                return f"OK Task {task_id} deleted\n"
            else:
                return "ERROR Task ID not found\n"
        except ValueError:
            return "ERROR Invalid ID format\n"
            
    return "ERROR Invalid command\n"

async def handle_client(reader, writer):
    peername = writer.get_extra_info('peername')
    print(f"[NEW CONNECTION] {peername}")
    
    try:
        while True:
            # Yield control back to the event loop while waiting for data
            data = await reader.read(1024)
            
            # If data is empty, the client cleanly disconnected
            if not data:
                break
                
            message = data.decode()
            print(f"[{peername}] Received: {message.strip()}")
            
            # Process the command
            response = parse_command(message, str(peername))
            
            # Send the response back
            writer.write(response.encode())
            await writer.drain() # Ensure the data is actually pushed out to the network
            
    except ConnectionResetError:
        print(f"[ERROR] Connection reset by {peername}")
    finally:
        print(f"[DISCONNECT] {peername}")
        writer.close()
        await writer.wait_closed()

async def main():
    # 0.0.0.0 binds to all available interfaces (localhost + your lab IP)
    server = await asyncio.start_server(handle_client, '0.0.0.0', 5055)

    addr = server.sockets[0].getsockname()
    print(f"Server serving on {addr}")

    # Keep the server running indefinitely
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    # Standard Python entry point for asyncio programs
    asyncio.run(main())