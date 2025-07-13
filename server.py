import socket
import threading
import os
import json
import gzip
import time
import sys
from datetime import datetime

# Default configuration
DEFAULT_CONFIG = {
    "server": {
        "host": "0.0.0.0",
        "port": 55555,
        "password": "",
        "interactive_password_setup": True
    },
    "file_transfer": {
        "upload_dir": "uploads",
        "buffer_size": 65536,
        "max_file_size": 104857600  # 100MB
    },
    "logging": {
        "enable_logging": True,
        "log_level": "INFO"
    }
}

CONFIG_FILE = "server_config.json"

def create_default_config():
    """Create default configuration file"""
    print("Configuration file not found, creating default configuration file...")
    
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=4)
        
        print(f"✅ Default configuration file created: {CONFIG_FILE}")
        print("\nPlease modify the settings in the configuration file as needed:")
        print("- server.host: Server listening address (0.0.0.0 means listen on all interfaces)")
        print("- server.port: Server port number")
        print("- server.password: Server password (empty string means no password)")
        print("- server.interactive_password_setup: Whether to enable interactive password setup")
        print("- file_transfer.upload_dir: File upload directory")
        print("- file_transfer.buffer_size: Transfer buffer size")
        print("- file_transfer.max_file_size: Maximum file size limit")
        print("\nPlease restart the server program after modification.")
        
        return False
    except Exception as e:
        print(f"❌ Failed to create configuration file: {e}")
        return False

def load_config():
    """Load configuration file"""
    if not os.path.exists(CONFIG_FILE):
        return create_default_config()
    
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        # Validate configuration file structure
        required_keys = ["server", "file_transfer"]
        for key in required_keys:
            if key not in config:
                print(f"❌ Configuration file missing required '{key}' section")
                return False
        
        print(f"✅ Configuration file loaded successfully: {CONFIG_FILE}")
        return config
        
    except json.JSONDecodeError as e:
        print(f"❌ Configuration file format error: {e}")
        print("Please check if the JSON format is correct")
        return False
    except Exception as e:
        print(f"❌ Failed to load configuration file: {e}")
        return False

# Load configuration
config = load_config()
if not config:
    sys.exit(1)

# Read settings from configuration file
SERVER_HOST = config["server"]["host"]
SERVER_PORT = config["server"]["port"]
SERVER_PASSWORD = config["server"]["password"]
INTERACTIVE_PASSWORD_SETUP = config["server"]["interactive_password_setup"]
UPLOAD_DIR = config["file_transfer"]["upload_dir"]
BUFFER_SIZE = config["file_transfer"]["buffer_size"]
METADATA_FILE = os.path.join(UPLOAD_DIR, "file_metadata.json")

# Display loaded configuration information
print(f"📋 Server Configuration:")
print(f"   Listen Address: {SERVER_HOST}")
print(f"   Listen Port: {SERVER_PORT}")
print(f"   Upload Directory: {UPLOAD_DIR}")
print(f"   Buffer Size: {BUFFER_SIZE}")
print(f"   Interactive Password Setup: {'Enabled' if INTERACTIVE_PASSWORD_SETUP else 'Disabled'}")

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
    print(f"📁 Created upload directory: {UPLOAD_DIR}")

# Global variables
clients = []
nicknames = []
uploaded_files = []


def load_file_metadata():
    global uploaded_files
    try:
        if os.path.exists(METADATA_FILE):
            with open(METADATA_FILE, "r", encoding="utf-8") as f:
                uploaded_files = json.load(f)
        print(f"Loaded metadata for {len(uploaded_files)} files")
    except Exception as e:
        print(f"\033[91mFailed to load metadata: {e}\033[0m")
        uploaded_files = []


def save_file_metadata():
    try:
        with open(METADATA_FILE, "w", encoding="utf-8") as f:
            json.dump(uploaded_files, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"\033[91mFailed to save metadata: {e}\033[0m")


def sync_files_and_metadata():
    global uploaded_files
    try:
        if not os.path.exists(UPLOAD_DIR):
            uploaded_files = []
            save_file_metadata()
            return
        existing_files = set()
        for filename in os.listdir(UPLOAD_DIR):
            if filename != "file_metadata.json" and os.path.isfile(
                os.path.join(UPLOAD_DIR, filename)
            ):
                existing_files.add(filename)
        original_count = len(uploaded_files)
        uploaded_files[:] = [
            f for f in uploaded_files if f["unique_filename"] in existing_files
        ]
        if len(uploaded_files) != original_count:
            save_file_metadata()
            print(
                f"Folder sync complete: cleaned {original_count - len(uploaded_files)} invalid records"
            )
            print(f"Current valid files: {len(uploaded_files)}")

    except Exception as e:
        print(f"\033[91mFailed to sync files and metadata: {e}\033[0m")


def initialize_server():
    global SERVER_PASSWORD, server
    print("\033[92mInitializing server...\033[0m")
    
    # If no password is set in config file and interactive setup is enabled, prompt user for input
    if not SERVER_PASSWORD and INTERACTIVE_PASSWORD_SETUP:
        password_input = input(
            "\033[93mPlease set the server password (press Enter for no password): \033[0m"
        ).strip()
        if password_input:
            SERVER_PASSWORD = password_input
            print(f"Password has been set (length: {len(SERVER_PASSWORD)})")
        else:
            print("No password mode - anyone can connect")
    
    if SERVER_PASSWORD:
        print(f"Server password authentication: ENABLED")
    else:
        print(f"Server password authentication: DISABLED")
    
    # Create and bind socket
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow port reuse
        server.bind((SERVER_HOST, SERVER_PORT))
        server.listen()
        print(f"🚀 Server started successfully, listening on {SERVER_HOST}:{SERVER_PORT}")
    except OSError as e:
        if e.errno == 10048:  # Windows: Address already in use
            print(f"❌ Port {SERVER_PORT} is already in use, please check if another program is using this port")
        elif e.errno == 10049:  # Windows: Cannot assign requested address
            print(f"❌ Cannot bind to address {SERVER_HOST}, please check network configuration")
        else:
            print(f"❌ Server startup failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        sys.exit(1)
    
    load_file_metadata()
    sync_files_and_metadata()


def broadcast(message):
    for client in clients:
        try:
            client.send(message)
        except:
            pass


def send_file_list(client):
    global uploaded_files
    try:
        files = []
        existing_files = set()
        if os.path.exists(UPLOAD_DIR):
            for filename in os.listdir(UPLOAD_DIR):
                if filename == "file_metadata.json":  # Ignore metadata file
                    continue
                file_path = os.path.join(UPLOAD_DIR, filename)
                if os.path.isfile(file_path):
                    existing_files.add(filename)
                    file_stats = os.stat(file_path)
                    file_size = file_stats.st_size
                    upload_time = datetime.fromtimestamp(file_stats.st_mtime).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    uploader = "Unknown"
                    original_filename = filename
                    original_size = file_size
                    for stored_file in uploaded_files:
                        if stored_file["unique_filename"] == filename:
                            uploader = stored_file["uploader"]
                            original_filename = stored_file["filename"]
                            original_size = stored_file.get("size", file_size)
                            break
                    if uploader == "Unknown" and "_" in filename:
                        original_filename = "_".join(filename.split("_")[1:])
                    file_info = {
                        "filename": original_filename,
                        "unique_filename": filename,
                        "uploader": uploader,
                        "upload_time": upload_time,
                        "size": original_size,
                        "compressed_size": file_size,
                    }
                    files.append(file_info)
        original_count = len(uploaded_files)
        uploaded_files[:] = [
            f for f in uploaded_files if f["unique_filename"] in existing_files
        ]
        if len(uploaded_files) != original_count:
            save_file_metadata()
            print(
                f"Cleaned {original_count - len(uploaded_files)} metadata records for non-existent files"
            )
        files.sort(key=lambda x: x["upload_time"], reverse=True)
        file_list = {"type": "file_list", "files": files}
        message = json.dumps(file_list).encode("utf-8")
        client.send(f"FILE_LIST:{len(message)}:".encode("utf-8") + message)

    except Exception as e:
        print(f"\033[91mError sending file list: {e}\033[0m")
        empty_list = {"type": "file_list", "files": []}
        message = json.dumps(empty_list).encode("utf-8")
        client.send(f"FILE_LIST:{len(message)}:".encode("utf-8") + message)


def handle_file_upload(client, filename, file_size, uploader):
    try:
        compressed_data = b""
        bytes_received = 0
        while bytes_received < file_size:
            chunk_size = min(BUFFER_SIZE, file_size - bytes_received)
            chunk = client.recv(chunk_size)
            if not chunk:
                break
            compressed_data += chunk
            bytes_received += len(chunk)
        file_data = gzip.decompress(compressed_data)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        with open(file_path, "wb") as f:
            f.write(file_data)
        file_info = {
            "filename": filename,
            "unique_filename": unique_filename,
            "uploader": uploader,
            "upload_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "size": len(file_data),
            "compressed_size": len(compressed_data),
        }
        uploaded_files[:] = [
            f for f in uploaded_files if f["unique_filename"] != unique_filename
        ]
        uploaded_files.append(file_info)
        save_file_metadata()
        notification = (
            f"{uploader} uploaded a file: {filename} (size: {len(file_data)} bytes)"
        )
        broadcast(notification.encode("utf-8"))

        # Send upload success message
        client.send("UPLOAD_SUCCESS".encode("utf-8"))
        print(
            f"File uploaded successfully: {filename} by {uploader} (original size: {len(file_data)}, compressed size: {len(compressed_data)})"
        )

    except Exception as e:
        client.send("UPLOAD_ERROR".encode("utf-8"))
        print(f"\033[91mFile upload error: {e}\033[0m")



def handle_file_download(client, unique_filename):
    try:
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                file_data = f.read()
            compressed_data = gzip.compress(file_data)
            file_info = {
                "type": "file_download",
                "filename": unique_filename,
                "size": len(file_data),
                "compressed_size": len(compressed_data),
            }

            info_json = json.dumps(file_info).encode("utf-8")
            client.send(f"FILE_INFO:{len(info_json)}:".encode("utf-8"))
            client.send(info_json)
            client.recv(1024)
            client.send(f"FILE_DATA_START:{len(compressed_data)}".encode("utf-8"))
            bytes_sent = 0
            while bytes_sent < len(compressed_data):
                chunk_size = min(BUFFER_SIZE, len(compressed_data) - bytes_sent)
                chunk = compressed_data[bytes_sent : bytes_sent + chunk_size]
                client.send(chunk)
                bytes_sent += chunk_size

            client.send("DOWNLOAD_COMPLETE".encode("utf-8"))
        else:
            client.send("FILE_NOT_FOUND".encode("utf-8"))
    except Exception as e:
        client.send("DOWNLOAD_ERROR".encode("utf-8"))



def handle(client):
    nickname = None
    try:
        nickname_index = clients.index(client)
        nickname = nicknames[nickname_index]
    except:
        pass

    while True:
        try:
            message = client.recv(1024)
            message_str = message.decode("utf-8")
            if message_str.startswith("UPLOAD_FILE:"):
                parts = message_str.split(":", 3)
                if len(parts) >= 4:
                    filename = parts[1]
                    file_size = int(parts[2])
                    handle_file_upload(client, filename, file_size, nickname)
                    continue
            elif message_str == "GET_FILE_LIST":
                send_file_list(client)
                continue
            elif message_str.startswith("DOWNLOAD_FILE:"):
                unique_filename = message_str.split(":", 1)[1]
                handle_file_download(client, unique_filename)
                continue
            else:
                broadcast(message)

        except:
            if client in clients:
                index = clients.index(client)
                clients.remove(client)
                client.close()
                if index < len(nicknames):
                    nickname = nicknames[index]
                    nicknames.remove(nickname)
                    broadcast(f"User {nickname} has left the chat room!".encode("utf-8"))
                    print(
                        f"\033[93mUser {nickname} has left, current online users: {len(clients)}\033[0m"
                    )
            break


# Handle new client connections
def receive():
    while True:
        client, address = server.accept()
        try:
            # Request nickname
            client.send("NICK".encode("utf-8"))
            nickname = client.recv(1024).decode("utf-8")
            
            # Request password
            client.send("PASS".encode("utf-8"))
            
            # Use length prefix method to receive password
            client.settimeout(3.0)  # 3秒超时
            client_password = ""
            try:
                # 先接收4字节的长度信息
                length_data = client.recv(4)
                if len(length_data) == 4:
                    password_length = int(length_data.decode("utf-8"))
                    if password_length > 0:
                        # 接收密码内容
                        password_data = client.recv(password_length)
                        client_password = password_data.decode("utf-8")
                    else:
                        # 密码长度为0，表示空密码
                        client_password = ""
                else:
                    print(f"\033[91mInvalid password length data from {nickname}\033[0m")
                    client_password = ""
            except socket.timeout:
                print(f"\033[93mPassword receive timeout for user {nickname}\033[0m")
                client_password = ""
            except Exception as e:
                print(f"\033[91mError receiving password from {nickname}: {e}\033[0m")
                client_password = ""
            finally:
                client.settimeout(None)  # 恢复阻塞模式
            
            # 密码验证逻辑
            auth_success = False
            if SERVER_PASSWORD:
                if client_password == SERVER_PASSWORD:
                    auth_success = True
                    print(f"User {nickname} from {address} authentication successful")
                else:
                    client.send("AUTH_FAILED".encode("utf-8"))
                    print(
                        f"User {nickname} from {address} authentication failed - wrong password (received: '{client_password}')"
                    )
                    client.close()
                    continue
            else:
                auth_success = True
                print(f"User {nickname} from {address} authentication successful (no password required)")
            
            # 验证成功
            if auth_success:
                client.send("AUTH_SUCCESS".encode("utf-8"))
                nicknames.append(nickname)
                clients.append(client)

                print(
                    f"\033[95mUser {nickname} from {str(address)} has connected, current online users: {len(clients)}\033[0m"
                )
                
                # 添加小延迟，确保AUTH_SUCCESS消息被客户端单独处理
                time.sleep(0.1)
                
                broadcast(f"{nickname} has joined the chat room!".encode("utf-8"))
                thread = threading.Thread(target=handle, args=(client,))
                thread.start()
                
        except Exception as e:
            print(f"\033[91mError handling client connection from {address}: {e}\033[0m")
            try:
                client.close()
            except:
                pass


# 启动服务器
if __name__ == "__main__":
    initialize_server()
    print("\033[92mServer is listening...\033[0m")
    try:
        receive()
    except KeyboardInterrupt:
        print("\n\033[93mServer is shutting down...\033[0m")
        server.close()
        print("\033[92mServer has been closed\033[0m")
    except Exception as e:
        print(f"\033[91mServer runtime error: {e}\033[0m")
        server.close()
