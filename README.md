# 🚀 Remote Exec Server & Client

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-green.svg)
![GitHub stars](https://img.shields.io/github/stars/foxhackerzdevs/remote-exec-server?style=social)
![GitHub forks](https://img.shields.io/github/forks/foxhackerzdevs/remote-exec-server?style=social)

**Lightweight Python-based remote command execution system**
*One client script, multiple symlinks, BusyBox-style.*

---

## 📖 Table of Contents

* [Overview](#overview)
* [Features](#features)
* [Architecture](#architecture)
* [Requirements](#requirements)
* [Quick Start](#quick-start)
* [Installation](#installation)
* [Configuration](#configuration)
* [Usage](#usage)
* [Protocol](#protocol)
* [Examples](#examples)
* [Security Considerations](#security-considerations)
* [Troubleshooting](#troubleshooting)
* [Project Structure](#project-structure)
* [Limitations](#limitations)
* [Future Improvements](#future-improvements)
* [Contributing](#contributing)
* [License](#license)

---

## Overview

Remote Exec Server & Client is a minimal remote command execution framework written entirely with the Python standard library.

The project consists of:

* **server.py** — receives HTTP requests and executes commands locally.
* **client.py** — forwards command invocations and standard input to the server.
* **BusyBox-style symlink support** — one client script can act as many commands depending on the name it is invoked under.

The design is intentionally lightweight and dependency-free.

---

## Features

* HTTP-based command forwarding
* Standard input (stdin) forwarding
* Command-line argument support
* BusyBox-style symlink invocation
* Works with any executable installed on the server
* No third-party dependencies
* Cross-platform Python implementation
* Minimal setup and deployment

---

## Architecture

```text
┌─────────────┐
│   Client    │
│  (symlink)  │
└──────┬──────┘
       │ HTTP POST
       ▼
┌─────────────┐
│   Server    │
│ server.py   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ subprocess  │
│ execution   │
└─────────────┘
       │
       ▼
┌─────────────┐
│   Output    │
└─────────────┘
```

---

## Requirements

* Python 3.8+
* Network connectivity between client and server

No external dependencies are required.

---

## ⚡ Quick Start

Start the server:

```bash
python server.py
```

Create a command symlink:

```bash
ln -s client.py gp
```

Execute a remote command:

```bash
echo "print(nextprime(100))" | ./gp -q
```

---

## Installation

### Server Setup

Copy `server.py` to the machine that will execute commands.

Run:

```bash
python server.py
```

Default listening address:

```text
0.0.0.0:8000
```

---

### Client Setup

Edit the server address:

```python
host = "SERVER_IP:8000"
```

Make executable:

```bash
chmod +x client.py
```

Place in your PATH:

```bash
cp client.py ~/bin/
```

Create command aliases:

```bash
ln -s ~/bin/client.py ~/bin/gp
ln -s ~/bin/client.py ~/bin/python
ln -s ~/bin/client.py ~/bin/node
```

Each symlink name becomes the command executed remotely.

---

## Configuration

### Client

Set the server host:

```python
host = "192.168.56.1:8000"
```

To enable HTTPS:

```python
http.client.HTTPSConnection
```

instead of:

```python
http.client.HTTPConnection
```

The server must also be configured for TLS.

---

### Server

Bind only to localhost:

```python
HTTPServer(("127.0.0.1", 8000), MyHandler)
```

Change port:

```python
HTTPServer(("0.0.0.0", 9000), MyHandler)
```

---

## Usage

### Basic Execution

```bash
command_name [arguments]
```

### With Standard Input

```bash
echo "input data" | command_name [arguments]
```

### Using Symlinks

```bash
ln -s client.py python
ln -s client.py node
ln -s client.py gp
```

The invoked name determines the command sent to the server.

---

## Protocol

The communication protocol is intentionally simple.

### Request

```http
POST /python script.py arg1 arg2 HTTP/1.1
Host: server:8000
Content-Type: text/plain
```

Body:

```text
stdin data goes here
```

---

### Server Processing

```python
cmd_parts = shlex.split(raw_path)
subprocess.run(cmd_parts, input=stdin_data)
```

---

### Response

```text
stdout output
```

or

```text
Error:
stderr output
```

---

## Examples

### Remote PARI/GP

```bash
echo "print(nextprime(100))" | gp -q
```

### Remote Python

```bash
echo "print('Hello World')" | python
```

### Remote Node.js

```bash
echo "console.log('hello from node')" | node
```

### Pass Arguments

```bash
echo "hello" | python script.py arg1 arg2
```

### Example Flow

User runs:

```bash
echo "print(2+2)" | python
```

Client sends:

```http
POST /python
```

Body:

```text
print(2+2)
```

Server executes:

```bash
python
```

Returns:

```text
4
```

---

## Security Considerations

> ⚠️ **WARNING**
>
> This project executes commands received over HTTP.
>
> Never expose the server directly to the public Internet without authentication, encryption, and access controls.

### Risks

* Arbitrary command execution
* Remote code execution (RCE)
* Unauthorized access
* Command abuse
* Resource exhaustion

### Recommended Protections

#### Command Whitelisting

```python
ALLOWED = {"python", "gp", "node"}

if cmd_parts[0] not in ALLOWED:
    output = f"Command not allowed: {cmd_parts[0]}"
    return
```

#### Network Restrictions

* VPN access only
* SSH tunnels
* Firewall allowlists
* Private networks

#### Authentication

Add:

* API keys
* Bearer tokens
* Mutual TLS
* Basic authentication

#### Isolation

Run commands:

* Inside Docker containers
* Inside restricted user accounts
* Inside sandboxes

#### Encryption

Use HTTPS/TLS whenever traffic crosses untrusted networks.

---

## Troubleshooting

### Connection Refused

Check:

```bash
python server.py
```

Verify:

* Server is running
* Correct IP address
* Correct port
* Firewall settings

---

### Command Not Found

Verify executable exists:

```bash
which python
which node
which gp
```

---

### Empty Output

Check:

* Server logs
* Command stdout/stderr behavior
* Input handling

---

### Wrong Host

Verify:

```python
host = "SERVER_IP:8000"
```

---

## Project Structure

```text
.
├── client.py
├── server.py
├── README.md
└── LICENSE
```

---

## Limitations

Current implementation:

* No authentication
* No TLS support by default
* No output streaming
* No concurrency
* No request validation
* No rate limiting
* No audit logging
* No file transfer support

These limitations are intentional to keep the code minimal.

---

## Future Improvements

* HTTPS/TLS support
* API-key authentication
* Mutual TLS
* Built-in command whitelists
* Output streaming
* Async request handling
* Docker deployment
* Audit logging
* Request signing
* Rate limiting
* File upload/download support

---

## Contributing

Contributions are welcome.

Potential contribution areas:

* Security enhancements
* Protocol improvements
* Testing
* Documentation
* Containerization
* Performance optimization

Open issues, submit pull requests, or fork the project.

---

## License

MIT License

See the `LICENSE` file for details.

---

<div align="center">

**Remote Exec Server & Client**

Minimal • Dependency-Free • BusyBox-Style • Python

</div>
