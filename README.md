# netdiag-toolkit

A modular network diagnostic and tooling suite built with Python. Designed for developers and network enthusiasts who want a clean, all-in-one GUI to inspect, test, and interact with their network environment.

---

## Features

| Module | Description |
|--------|-------------|
| **Machine Info** | Displays hostname, IP address, and all network interfaces with IPv4/IPv6 details |
| **Echo Test** | Runs a TCP echo server/client to verify connection integrity and data consistency |
| **SNTP Time Sync** | Fetches accurate time from an NTP server and displays it in real-time |
| **Chat Module** | Multi-client TCP chat with server/client mode, live messaging, and automatic chat log export |
| **Error & Settings Manager** | Configure socket timeout, buffer sizes, blocking mode, logging, and error handling — all persisted to disk |

---

## Interface Preview

The application features a modern dark-themed sidebar GUI built with `tkinter`. Each module loads dynamically inside the content area without relaunching the app.

---

## Project Structure

```
netdiag-toolkit/
├── src/
│   ├── interface.py        # Main GUI application (entry point)
│   ├── machineInfo.py      # Machine Info module
│   ├── Echomessage.py      # Echo Test module
│   ├── Sntpmodules.py      # SNTP Time Sync module
│   ├── Chatserver.py       # Chat server
│   ├── Chatclient.py       # Chat client
│   └── ErrSet.py           # Error & Settings module
├── .gitignore
├── requirements.txt
├── LICENSE
└── README.md
```

---

## Requirements

- Python 3.8+
- `netifaces`
- `psutil`

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Getting Started

```bash
# Clone the repository
git clone https://github.com/gizemezer/netdiag-toolkit.git
cd netdiag-toolkit

# Install dependencies
pip install -r requirements.txt

# Run the application
python src/interface.py
```

---

## Module Details

### Machine Info
Retrieves and displays the local machine's hostname, primary IP address, and a full breakdown of all network interfaces — including both IPv4 and IPv6 addresses — using `netifaces` and `psutil`.

### Echo Test
Spins up a TCP echo server on a configurable port. The client sends a message, the server echoes it back, and the module confirms whether the sent and received data match. Useful for validating basic socket connectivity.

### SNTP Time Sync
Sends a lightweight UDP request to a public NTP server (`0.uk.pool.ntp.org`) and parses the response to display the current network time. Demonstrates raw NTP packet construction and parsing with `struct`.

### Chat Module
A fully functional multi-client TCP chat system. The server uses `select()` for non-blocking I/O and broadcasts messages to all connected clients. Messages are serialized with `pickle` for structured transfer, and the server automatically saves a timestamped chat log on shutdown.

### Error & Settings Manager
Manages socket-level configuration: timeout, send/receive buffer sizes, blocking vs. non-blocking mode, logging toggle, and error handling toggle. All settings are persisted to `settings.txt` and loaded on startup. Errors and events are logged to `error_log.txt`.

---

## Notes

- Chat logs are saved as `chat_log_server_<timestamp>.txt` in the working directory (excluded from version control via `.gitignore`).
- Settings are stored in `settings.txt` and automatically loaded by the Echo and Error modules.
- The GUI is built entirely with Python's standard `tkinter` library — no external UI framework required.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
