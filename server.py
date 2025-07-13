import socket
import threading

# 服务器配置
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 55555

# 初始化服务器
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((SERVER_HOST, SERVER_PORT))
server.listen()

# 存储客户端和昵称
clients = []
nicknames = []

# 广播消息给所有客户端
def broadcast(message):
    for client in clients:
        client.send(message)

# 处理客户端连接
def handle(client):
    while True:
        try:
            # 接收客户端消息
            message = client.recv(1024)
            broadcast(message)
        except:
            # 处理客户端断开连接
            index = clients.index(client)
            clients.remove(client)
            client.close()
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