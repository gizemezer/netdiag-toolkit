import socket#for network communication
import time#for time-related operations
import os#for operating system operations


SETTINGS_FILE = "settings.txt"#filename where settings saved
LOG_FILE = "error_log.txt"#filename where error logs

#all socket settings in dictionary
settings = {
    "timeout": None,
    "send_buf": 4096,
    "recv_buf": 4096,
    "blocking": True,
    "enable_logging": True,
    "handle_errors": True
}

def write_log(msg):
    # Function to write general log messages
    if not settings.get("enable_logging", True):
        return
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{now}] {msg}\n")

def write_error_log(msg):
    #error logs specifically for Error Manager
    if not settings.get("enable_logging", True):
        return
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{now}] [ERROR_MANAGER] {msg}\n")


def load():
# Function to load settings from settings.txt file
    if not os.path.exists(SETTINGS_FILE):
        return
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=")
                    # Checks if the key exists
                    if k in settings:
                        if v == "None":
                            settings[k] = None
                        elif v in ["True", "False"]:
                            settings[k] = v == "True"
                        elif "." in v:
                            settings[k] = float(v)
                        else:
                            settings[k] = int(v)
        write_log("Settings loaded.")
    # Catches any exception that occurs during the process
    except Exception as e:
        if settings.get("handle_errors", True):
            write_log(f"Error loading settings: {e}")


def save():
    #to save current settings to settings.txt file
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            for k, v in settings.items():
                f.write(f"{k}={v}\n")

        write_error_log(
            f"Timeout: {settings['timeout']}, Send Buffer: {settings['send_buf']}, Receive Buffer: {settings['recv_buf']}, Blocking: {settings['blocking']}, Logging: {settings['enable_logging']}, Error Handling: {settings['handle_errors']}")
    except Exception as e:
        if settings.get("handle_errors", True):
            write_error_log(f"Error saving settings: {e}")


def apply(sock):
    #apply current settings to a socket object
    try:
        if settings["timeout"] is not None:
            sock.settimeout(settings["timeout"])

        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, settings["send_buf"])
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, settings["recv_buf"])

        sock.setblocking(settings["blocking"])
    except Exception as e:
        if settings.get("handle_errors", True):
            write_log(f"Error applying socket settings: {e}")

def change_timeout():
    #to change timeoyt value
    val = input("Timeout (seconds) or 'none': ")
    settings["timeout"] = None if val.lower() == "none" else float(val)
    save()

def change_buffers():
    #to change buffer sizes
    settings["send_buf"] = int(input("Send buffer (bytes): "))
    settings["recv_buf"] = int(input("Receive buffer (bytes): "))
    save()


def change_blocking():
    #to cahnge nloking mode
    mode = input("Blocking? (1=Yes, 0=No): ")
    settings["blocking"] = mode == "1"
    save()

def set_logging():
    #to change logging setting
    val = input("")
    if val == "0":
        settings["enable_logging"] = False
    elif val == "1":
        settings["enable_logging"] = True
        return
    print("Loglama durumu:", "Açık" if settings["enable_logging"] else "Kapalı")
    save()

def set_error_handling():
    #to change error handling mode
    val = input(" ")
    if val == "0":
        settings["handle_errors"] = False
    elif val == "1":
        settings["handle_errors"] = True
        return
    print("Hata yakalama durumu:", "Açık" if settings["handle_errors"] else "Kapalı")
    save()

def test():
   #to test network connection with current settings
    host = input("Server IP: ")
    port = int(input("Port: "))
    try:#to handle potential connection errors
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        apply(s)
        s.connect((host, port))
        s.send(b"test")
        data = s.recv(1024)
        print("Connected. Got:", data)
        write_log("Connection OK.")
        s.close()

    except socket.timeout:# Catches timeout exceptions specifically
        print("Timeout!")
        write_log("Timeout error.")
    except Exception as e: # Catches all other exceptions
        print("Error:", e)
        if settings.get("handle_errors", True):
            write_log(f"Connection error: {e}")



