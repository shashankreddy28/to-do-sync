import asyncio

# Global state
tasks = {}
task_id_counter = 1 # Acts as our unique primary key generator
# Add this near your tasks and task_id_counter
active_clients = set()
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
        response = f"OK Task added ID={task_id}\n"
        broadcast_msg = f"UPDATE: {peername} added task: {text}\n"
        return (response, broadcast_msg)

    elif command == "VIEW":
        if not tasks:
            response = "LIST EMPTY\n"
        else:
            response = "LIST\n"
            for t_id, task in tasks.items():
                response += f"{t_id}: {task['text']} (from {task['owner']})\n"
        return (response, None)

    elif command == "DELETE" and len(parts) > 1:
        try:
            task_id = int(parts[1])
            if task_id in tasks:
                del tasks[task_id]
                response = f"OK Task {task_id} deleted\n"
                broadcast_msg = f"UPDATE: {peername} deleted task ID {task_id}\n"
                return (response, broadcast_msg)
            else:
                return ("ERROR Task ID not found\n", None)
        except ValueError:
            return ("ERROR Invalid ID format\n", None)
            
    return ("ERROR Invalid command\n", None)

async def handle_client(reader, writer):
    peername = writer.get_extra_info('peername')
    print(f"[NEW CONNECTION] {peername}")
    
    active_clients.add(writer)  # Register the client
    
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
            response, broadcast_msg = parse_command(message, str(peername))
            
            # Send the response back
            writer.write(response.encode())
            await writer.drain() # Ensure the data is actually pushed out to the network
            
            # Broadcast update to other clients if there's a message
            if broadcast_msg:
                await broadcast(broadcast_msg, exclude_writer=writer)
            
    except ConnectionResetError:
        print(f"[ERROR] Connection reset by {peername}")
    finally:
        print(f"[DISCONNECT] {peername}")
        active_clients.discard(writer)  # Unregister on disconnect
        writer.close()
        await writer.wait_closed()

async def broadcast(message, exclude_writer=None):
    """Sends a message to all connected clients, optionally excluding the sender."""
    if not active_clients:
        return
        
    encoded_message = message.encode()
    for writer in active_clients:
        if writer != exclude_writer:
            try:
                writer.write(encoded_message)
                await writer.drain()
            except Exception as e:
                print(f"[ERROR] Broadcast failed to a client: {e}")

async def main():
    try:
        # 0.0.0.0 binds to all available interfaces (localhost + your lab IP)
        server = await asyncio.start_server(handle_client, '0.0.0.0', 5055)

        addr = server.sockets[0].getsockname()
        print(f"Server serving on {addr}")

        # Keep the server running indefinitely
        async with server:
            await server.serve_forever()
    except KeyboardInterrupt:
        print("\n[SERVER] Shutdown signal received. Closing gracefully...")

if __name__ == "__main__":
    # Standard Python entry point for asyncio programs
    asyncio.run(main())