import asyncio
from logging_setup import setup_logging

# Global state
tasks = {}
task_id_counter = 1 # Acts as our unique primary key generator
active_clients = set() # Tracks connected clients for broadcasting

# Initialize logger
logger = setup_logging('server')

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
        
        # Spec: OK <id>\r\n
        response = f"OK {task_id}\r\n"
        broadcast_msg = f"UPDATE: {peername} added task: {text}\r\n"
        return (response, broadcast_msg)

    elif command == "VIEW":
        if not tasks:
            response = "LIST \r\n"
        else:
            # Spec: LIST <id>:<task>; <id>:<task>; ...\r\n
            task_strings = [f"{t_id}:{task['text']}" for t_id, task in tasks.items()]
            response = f"LIST {'; '.join(task_strings)}\r\n"
        return (response, None)

    elif command == "DELETE" and len(parts) > 1:
        try:
            task_id = int(parts[1])
            if task_id in tasks:
                del tasks[task_id]
                # Spec: OK\r\n
                response = "OK\r\n"
                broadcast_msg = f"UPDATE: {peername} deleted task ID {task_id}\r\n"
                return (response, broadcast_msg)
            else:
                # Spec: ERROR Task ID not found\r\n
                return ("ERROR Task ID not found\r\n", None)
        except ValueError:
            return ("ERROR Invalid command\r\n", None)
            
    # Spec: ERROR Invalid command\r\n
    return ("ERROR Invalid command\r\n", None)

async def handle_client(reader, writer):
    peername = writer.get_extra_info('peername')
    print(f"[NEW CONNECTION] {peername}")
    logger.info(f"New client connected: {peername}")
    
    active_clients.add(writer)  # Register the client
    logger.info(f"Client {peername} added to active clients.")
    logger.info(f"Active clients count: {len(active_clients)}")
    
    try:
        while True:
            data = await reader.read(1024)
            
            if not data:
                break
                
            message = data.decode()
            print(f"[{peername}] Received: {message.strip()}")
            logger.info(f"Received message from {peername}: {message.strip()}")
            
            response, broadcast_msg = parse_command(message, str(peername))
            logger.info(f"Sending response to {peername}: {response.strip()}")
            
            writer.write(response.encode())
            await writer.drain() 
            
            if broadcast_msg:
                await broadcast(broadcast_msg, exclude_writer=writer)
            
    except ConnectionResetError:
        print(f"[ERROR] Connection reset by {peername}")
        logger.error(f"Connection reset by {peername}")
    finally:
        print(f"[DISCONNECT] {peername}")
        logger.info(f"Client {peername} disconnected.")
        active_clients.discard(writer)  # Unregister on disconnect
        writer.close()
        await writer.wait_closed()

async def broadcast(message, exclude_writer=None):
    """Sends a message to all connected clients, optionally excluding the sender."""
    if not active_clients:
        return
        
    encoded_message = message.encode()
    logger.info(f"Broadcasting message to clients: {message.strip()}")
    for writer in active_clients:
        if writer != exclude_writer:
            try:
                writer.write(encoded_message)
                await writer.drain()
            except Exception as e:
                print(f"[ERROR] Broadcast failed to a client: {e}")
                logger.error(f"Broadcast failed to a client: {e}")

async def main():
    # 0.0.0.0 binds to all available interfaces
    server = await asyncio.start_server(handle_client, '0.0.0.0', 5055)

    addr = server.sockets[0].getsockname()
    print(f"Server serving on {addr}")
    logger.info(f"Server started on {addr}")

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    # Move the try/except block here. asyncio.run() manages the event loop,
    # so the KeyboardInterrupt gets thrown at this level, not inside main().
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[SERVER] Shutdown signal received. Closing gracefully...")
        logger.info("Server shutdown initiated by user.")