import socket
import threading
import os
import json
import base64
import gzip
from datetime import datetime

# 服务器配置
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 55555
BUFFER_SIZE = 65536  # 64KB缓冲区，提高传输速度

# 文件存储目录
UPLOAD_DIR = "uploads"
METADATA_FILE = os.path.join(UPLOAD_DIR, "file_metadata.json")

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# 初始化服务器
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((SERVER_HOST, SERVER_PORT))
server.listen()

# 存储客户端和昵称
clients = []
nicknames = []
uploaded_files = []  # 存储已上传的文件信息

# 加载文件元数据
def load_file_metadata():
    """从元数据文件中加载文件信息"""
    global uploaded_files
    try:
        if os.path.exists(METADATA_FILE):
            with open(METADATA_FILE, 'r', encoding='utf-8') as f:
                uploaded_files = json.load(f)
        print(f"加载了 {len(uploaded_files)} 个文件的元数据")
    except Exception as e:
        print(f"加载元数据失败: {e}")
        uploaded_files = []

# 保存文件元数据
def save_file_metadata():
    """保存文件元数据到文件"""
    try:
        with open(METADATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(uploaded_files, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存元数据失败: {e}")

# 同步文件夹和元数据
def sync_files_and_metadata():
    """同步文件夹内容和元数据，移除不存在文件的记录"""
    global uploaded_files
    
    try:
        if not os.path.exists(UPLOAD_DIR):
            uploaded_files = []
            save_file_metadata()
            return
        
        # 获取实际存在的文件
        existing_files = set()
        for filename in os.listdir(UPLOAD_DIR):
            if filename != "file_metadata.json" and os.path.isfile(os.path.join(UPLOAD_DIR, filename)):
                existing_files.add(filename)
        
        # 清理元数据：只保留实际存在的文件
        original_count = len(uploaded_files)
        uploaded_files[:] = [f for f in uploaded_files if f['unique_filename'] in existing_files]
        
        # 如果有变化，保存元数据
        if len(uploaded_files) != original_count:
            save_file_metadata()
            print(f"文件夹同步完成: 清理了 {original_count - len(uploaded_files)} 个无效记录")
            print(f"当前有效文件: {len(uploaded_files)} 个")
        
    except Exception as e:
        print(f"同步文件和元数据失败: {e}")

# 启动时进行文件同步
def initialize_server():
    """初始化服务器，加载并同步文件"""
    print("正在初始化服务器...")
    load_file_metadata()
    sync_files_and_metadata()
    print("服务器初始化完成")

# 启动时调用初始化
initialize_server()

# 广播消息给所有客户端
def broadcast(message):
    for client in clients:
        try:
            client.send(message)
        except:
            pass

# 发送文件列表给客户端（从真实文件夹读取并同步元数据）
def send_file_list(client):
    global uploaded_files
    try:
        # 直接从uploads文件夹扫描文件
        files = []
        existing_files = set()  # 用于跟踪实际存在的文件
        
        if os.path.exists(UPLOAD_DIR):
            for filename in os.listdir(UPLOAD_DIR):
                # 跳过元数据文件
                if filename == "file_metadata.json":
                    continue
                    
                file_path = os.path.join(UPLOAD_DIR, filename)
                if os.path.isfile(file_path):
                    existing_files.add(filename)
                    
                    # 获取文件信息
                    file_stats = os.stat(file_path)
                    file_size = file_stats.st_size
                    upload_time = datetime.fromtimestamp(file_stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                    
                    # 从元数据中查找文件信息
                    uploader = "未知"
                    original_filename = filename
                    original_size = file_size
                    
                    for stored_file in uploaded_files:
                        if stored_file['unique_filename'] == filename:
                            uploader = stored_file['uploader']
                            original_filename = stored_file['filename']
                            original_size = stored_file.get('size', file_size)
                            break
                    
                    # 如果没有在元数据中找到，尝试从文件名解析
                    if uploader == "未知" and '_' in filename:
                        original_filename = '_'.join(filename.split('_')[1:])
                    
                    file_info = {
                        "filename": original_filename,
                        "unique_filename": filename,
                        "uploader": uploader,
                        "upload_time": upload_time,
                        "size": original_size,
                        "compressed_size": file_size  # 磁盘上的就是压缩后的大小
                    }
                    files.append(file_info)
        
        # 清理元数据：移除不存在的文件记录
        original_count = len(uploaded_files)
        uploaded_files[:] = [f for f in uploaded_files if f['unique_filename'] in existing_files]
        
        # 如果有文件被清理，保存更新后的元数据
        if len(uploaded_files) != original_count:
            save_file_metadata()
            print(f"清理了 {original_count - len(uploaded_files)} 个不存在文件的元数据记录")
        
        # 按上传时间排序（最新的在前）
        files.sort(key=lambda x: x['upload_time'], reverse=True)
        
        file_list = {
            "type": "file_list", 
            "files": files
        }
        message = json.dumps(file_list).encode('utf-8')
        client.send(f"FILE_LIST:{len(message)}:".encode('utf-8') + message)
        print(f"发送文件列表: 共 {len(files)} 个文件")
        
    except Exception as e:
        print(f"发送文件列表错误: {e}")
        # 发送空列表作为备用
        empty_list = {"type": "file_list", "files": []}
        message = json.dumps(empty_list).encode('utf-8')
        client.send(f"FILE_LIST:{len(message)}:".encode('utf-8') + message)

# 处理文件上传（修复版本）
def handle_file_upload(client, filename, file_size, uploader):
    try:
        # 接收压缩的文件数据
        compressed_data = b""
        bytes_received = 0
        
        while bytes_received < file_size:
            chunk_size = min(BUFFER_SIZE, file_size - bytes_received)
            chunk = client.recv(chunk_size)
            if not chunk:
                break
            compressed_data += chunk
            bytes_received += len(chunk)
        
        # 解压缩文件数据
        file_data = gzip.decompress(compressed_data)
        
        # 生成唯一文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # 保存文件
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        # 添加到文件列表并保存元数据
        file_info = {
            "filename": filename,
            "unique_filename": unique_filename,
            "uploader": uploader,
            "upload_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "size": len(file_data),
            "compressed_size": len(compressed_data)
        }
        
        # 更新内存中的文件列表
        # 先移除可能存在的同名文件记录
        uploaded_files[:] = [f for f in uploaded_files if f['unique_filename'] != unique_filename]
        uploaded_files.append(file_info)
        
        # 保存元数据到文件
        save_file_metadata()
        
        # 通知所有客户端有新文件上传
        notification = f"{uploader} 上传了文件: {filename} (大小: {len(file_data)} 字节)"
        broadcast(notification.encode('utf-8'))
        
        # 发送上传成功消息
        client.send("UPLOAD_SUCCESS".encode('utf-8'))
        print(f"文件上传成功: {filename} by {uploader} (原始大小: {len(file_data)}, 压缩大小: {len(compressed_data)})")
        
    except Exception as e:
        client.send("UPLOAD_ERROR".encode('utf-8'))
        print(f"文件上传错误: {e}")

# 处理文件下载（修复版本）
def handle_file_download(client, unique_filename):
    try:
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        if os.path.exists(file_path):
            # 读取并压缩文件
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            compressed_data = gzip.compress(file_data)
            
            # 发送文件信息
            file_info = {
                "type": "file_download",
                "filename": unique_filename,
                "size": len(file_data),
                "compressed_size": len(compressed_data)
            }
            
            info_json = json.dumps(file_info).encode('utf-8')
            
            # 先发送文件信息
            client.send(f"FILE_INFO:{len(info_json)}:".encode('utf-8'))
            client.send(info_json)
            
            # 等待客户端确认
            client.recv(1024)  # 等待 "READY" 确认
            
            # 分块发送压缩数据
            client.send(f"FILE_DATA_START:{len(compressed_data)}".encode('utf-8'))
            
            bytes_sent = 0
            while bytes_sent < len(compressed_data):
                chunk_size = min(BUFFER_SIZE, len(compressed_data) - bytes_sent)
                chunk = compressed_data[bytes_sent:bytes_sent + chunk_size]
                client.send(chunk)
                bytes_sent += chunk_size
            
            client.send("DOWNLOAD_COMPLETE".encode('utf-8'))
            print(f"文件下载成功: {unique_filename}")
        else:
            client.send("FILE_NOT_FOUND".encode('utf-8'))
    except Exception as e:
        client.send("DOWNLOAD_ERROR".encode('utf-8'))
        print(f"文件下载错误: {e}")
        print(f"文件下载错误: {e}")

# 处理客户端连接
def handle(client):
    nickname = None
    try:
        nickname_index = clients.index(client)
        nickname = nicknames[nickname_index]
    except:
        pass
        
    while True:
        try:
            # 接收客户端消息
            message = client.recv(1024)
            message_str = message.decode('utf-8')
            
            # 处理文件上传请求
            if message_str.startswith("UPLOAD_FILE:"):
                parts = message_str.split(":", 3)
                if len(parts) >= 4:
                    filename = parts[1]
                    file_size = int(parts[2])
                    
                    handle_file_upload(client, filename, file_size, nickname)
                    continue
            
            # 处理文件列表请求
            elif message_str == "GET_FILE_LIST":
                send_file_list(client)
                continue
            
            # 处理文件下载请求
            elif message_str.startswith("DOWNLOAD_FILE:"):
                unique_filename = message_str.split(":", 1)[1]
                handle_file_download(client, unique_filename)
                continue
            
            # 普通聊天消息
            else:
                broadcast(message)
                
        except:
            # 处理客户端断开连接
            if client in clients:
                index = clients.index(client)
                clients.remove(client)
                client.close()
                if index < len(nicknames):
                    nickname = nicknames[index]
                    nicknames.remove(nickname)
                    broadcast(f'{nickname} 已离开聊天室！'.encode('utf-8'))
                    print(f'User {nickname} has left, current online users: {len(clients)}')
            break

# 接收新的客户端连接
def receive():
    while True:
        client, address = server.accept()

        # 接收客户端昵称
        client.send('NICK'.encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')
        nicknames.append(nickname)
        clients.append(client)

        print(f'\033[95mUser {nickname}{str(address)} has connected, current online users: {len(clients)}\033[0m')
        broadcast(f'{nickname} 已加入聊天室！'.encode('utf-8'))
        client.send('已连接到服务器！'.encode('utf-8'))

        # 为每个客户端启动一个线程
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

print('\033[92mServer is listening...\033[0m')
receive()