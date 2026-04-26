# Shared To-Do List - TCP Server

This repository contains the backend server for our networking capstone project. The server uses Python's `asyncio` to handle multiple concurrent TCP connections.

## Setup

Only first time: Create venv: `python3 -m venv venv`

Activate evn: Mac: `source venv/bin/activate` Windows: `venv\Scripts\activate`

If facing dependency issues while running: `pip freeze > requirements.txt` (update your env)

MAKE SURE TO UPDATE requirements.txt WITH ANY NEW LIBRARIES USED.

## The Protocol (Current State)
The server currently listens on port `5055` and accepts the following plain-text commands:

* `ADD <text>`: Creates a new task. Returns `OK Task added ID=<id>`.
* `VIEW`: Returns a list of all current tasks or `LIST EMPTY`.
* `DELETE <id>`: Deletes a specific task. Returns `OK` or an `ERROR` message.

## Running the Server Locally
1. Activate your virtual environment.
2. Run the server: `python server.py`
3. The server will output `Server serving on ('0.0.0.0', 5055)` and log new connections.