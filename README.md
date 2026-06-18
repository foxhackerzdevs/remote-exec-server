# 🚀 Remote Exec Server & Client

A lightweight Python-based remote command execution system consisting of:

- **server.py** — Executes commands received over HTTP.
- **client.py** — Forwards local command invocations and stdin to the remote server.

The design is inspired by the BusyBox model, where a single client script can be invoked under multiple names via symlinks, allowing remote execution of different programs transparently.

---

# Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
  - [Server Setup](#server-setup)
  - [Client Setup](#client-setup)
- [Usage](#usage)
- [Examples](#examples)
- [Configuration](#configuration)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)
- [Future Improvements](#future-improvements)
- [License](#license)

---

# Overview

This project allows commands to be executed on a remote machine through a simple HTTP interface.

The client:

1. Detects the command name it was invoked as.
2. Reads command-line arguments and standard input.
3. Sends the request to the remote server.

The server:

1. Receives the request.
2. Decodes the command and arguments.
3. Executes the command locally using `subprocess.run()`.
4. Returns stdout back to the client.

This makes it possible to run software remotely from systems where the software is not installed.

Example use cases:

- Running PARI/GP remotely
- Running scripts on a dedicated compute machine
- Accessing tools installed only on a server
- Thin-client command forwarding

---

# Architecture

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
````

---

# Features

* Simple HTTP-based protocol
* Supports stdin forwarding
* Supports command-line arguments
* Works with any executable available on the server
* Single client script can emulate multiple commands via symlinks
* Minimal dependencies (Python standard library only)

---

# Requirements

* Python 3.8+
* Network connectivity between client and server

No third-party Python packages are required.

---

# Installation

## Server Setup

Copy `server.py` to the machine that will execute commands.

Start the server:

```bash
python server.py
```

Default bind address:

```text
0.0.0.0:8000
```

---

## Client Setup

Edit the host setting:

```python
host = "192.168.56.1:8000"
```

Make the script executable:

```bash
chmod +x client.py
```

Install somewhere in your PATH:

```bash
cp client.py ~/bin/
```

---

### Create Command Symlinks

Example:

```bash
ln -s ~/bin/client.py ~/bin/gp
ln -s ~/bin/client.py ~/bin/python
ln -s ~/bin/client.py ~/bin/node
```

When invoked through a symlink, the client forwards that command name to the server.

---

# Usage

General form:

```bash
echo "input" | command_name [args]
```

Where `command_name` is a symlink pointing to `client.py`.

---

# Examples

## Run PARI/GP

```bash
echo "print(nextprime(100))" | gp -q
```

---

## Run Remote Python

```bash
echo "print('Hello World')" | python
```

---

## Pass Arguments

```bash
echo "hello" | python script.py
```

---

## Remote Node.js

```bash
echo "console.log('hello')" | node
```

---

# Configuration

## Client

Modify the server address:

```python
host = "192.168.56.1:8000"
```

For TLS-enabled deployments, replace:

```python
http.client.HTTPConnection
```

with:

```python
http.client.HTTPSConnection
```

---

## Server

Default bind configuration:

```python
HTTPServer(("0.0.0.0", 8000), MyHandler)
```

To restrict access to localhost:

```python
HTTPServer(("127.0.0.1", 8000), MyHandler)
```

---

# Security Considerations

⚠️ **This project executes arbitrary commands received over HTTP.**

Running the server on a public network is extremely dangerous.

## Recommended Protections

### Command Whitelist

Restrict executable commands:

```python
ALLOWED = {"gp", "python", "node"}

if cmd_parts[0] not in ALLOWED:
    output = f"Command not allowed: {cmd_parts[0]}"
    return
```

---

### Network Restrictions

Use:

* VPN access
* SSH tunnels
* Host-only networks
* Firewall rules

Avoid exposing the service directly to the Internet.

---

### TLS Encryption

Use HTTPS when transmitting over untrusted networks.

---

### Authentication

Consider adding:

* API keys
* Bearer tokens
* Mutual TLS
* IP allowlists

---

### Sandbox Execution

For higher security, run commands inside:

* Containers
* Virtual machines
* Chroot environments
* Restricted user accounts

---

# Troubleshooting

## Command Not Found

Error:

```text
Error: command not found
```

Ensure the executable exists on the server:

```bash
which python
which gp
which node
```

---

## Connection Refused

Verify:

```bash
python server.py
```

is running and listening on the configured port.

---

## No Output Returned

Check:

* Server logs
* Command permissions
* Whether the command writes only to stderr

---

## Incorrect Host Address

Verify:

```python
host = "SERVER_IP:8000"
```

matches the actual server address.

---

# Project Structure

```text
.
├── client.py
├── server.py
└── README.md
```

---

# Future Improvements

Potential enhancements:

* HTTPS support
* Authentication
* Command whitelisting
* Streaming output
* Async request handling
* File transfer support
* Rate limiting
* Logging and auditing
* Docker deployment

---

# License

MIT License

You are free to use, modify, and distribute this software under the terms of the MIT License.
