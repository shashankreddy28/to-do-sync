# 📋 Networking Capstone: Team Action Plan & Requirements

## 🧠 Project Overview
**Project:** TCP-Based Shared To-Do List  
**Protocol:** TCP only (per updated requirements)  

**Current Status:**  
- Member 1 has completed `server.py` using `asyncio`
- Server listens on **port 5055**
- Supports **multiple concurrent connections**

---

## 💻 Member 2: Client Application

### 🎯 Goal
Build a terminal-based interface for users to manage tasks.

### 🔌 Connection
- Use Python `asyncio`
- Connect to server via **TCP on port 5055**

### 🖥️ Interface
- Continuous CLI loop prompting user for actions

### 🔄 Command Mapping
| User Action | Command Sent | Expected Response |
|------------|-------------|-------------------|
| Add task | `ADD <text>` | `OK Task added ID=<id>` |
| View tasks | `VIEW` | `LIST\n<tasks>` |
| Delete task | `DELETE <id>` | `OK` or `ERROR` |

### 📤 Response Handling
- Format and display server responses cleanly in terminal

---

## 🛡️ Member 3: Error Handling & Resilience

### 🎯 Goal
Make the system stable and prevent crashes

### ⚠️ Client-Side (Network Errors)
- Catch `ConnectionRefusedError` (server down / wrong IP)
- Use `asyncio.wait_for()` for timeouts
- Catch `ConnectionResetError` (unexpected disconnects)

### ⚠️ Server-Side (Protocol Errors)
- Handle clean disconnects (`b''`)
- Validate inputs (e.g., reject `DELETE abc`, `EDIT 5`)
- Prevent crashes on malformed or empty messages

### 📝 Logging
- Use `logging` module (or structured `print`)
- Track:
  - New connections
  - Incoming messages
  - Errors

---

## 📄 Member 4: Protocol Specification & Infrastructure

### 🎯 Goal
Handle documentation and ensure demo setup works

### 📘 Protocol Document (Required Sections)

#### 1. High-Level Description
- Explain what the shared to-do list does
- Define the problem it solves

#### 2. Transport Choice
- Use **TCP**
- Justify (e.g., reliable delivery for task updates)

#### 3. Message Catalog
Document:
- Format
- Direction (Client → Server)
- Expected responses

Commands:
- `ADD`
- `VIEW`
- `DELETE`
