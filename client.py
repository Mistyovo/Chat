import tkinter as tk
from tkinter import simpledialog, messagebox
import socket
import threading

# 客户端配置
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 55555

# 创建主窗口（用于弹出输入框）
root = tk.Tk()
root.withdraw()  # 先隐藏主窗口

# 弹出输入昵称对话框
nickname = simpledialog.askstring('昵称', '请输入你的昵称:')
if not nickname:
    exit()

root.deiconify()  # 显示主窗口
root.title('聊天室')

# 初始化客户端变量
client = None

# 接收服务器消息
def receive():
    while True:
        try:
            # 接收服务器消息
            message = client.recv(1024).decode('utf-8')
            if message == 'NICK':
                client.send(nickname.encode('utf-8'))
            else:
                chat_box.config(state='normal')
                parts = message.split(': ', 1)
                if len(parts) > 1:
                    username, text = parts
                    chat_box.insert(tk.END, username, 'username')
                    chat_box.insert(tk.END, ': ' + text + '\n')
                else:
                    chat_box.insert(tk.END, message + '\n')
                chat_box.see(tk.END)  # 滚动到最新消息
                chat_box.config(state='disabled')
        except:
            # 处理连接错误
            messagebox.showerror("错误", "与服务器的连接已断开！")
            root.quit()
            break
        
# 发送消息给服务器
def send(event=None):
    message = input_box.get()
    if message.strip():  # 只发送非空消息
        input_box.delete(0, tk.END)
        full_message = f'{nickname}: {message}'
        client.send(full_message.encode('utf-8'))

# 创建聊天框
chat_box = tk.Text(root, state='disabled')
chat_box.tag_config('username', foreground='green')
chat_box.pack(fill=tk.X)

# 创建输入框
input_box = tk.Entry(root)
input_box.pack(side=tk.LEFT, fill=tk.X, expand=True)

# 创建发送按钮
send_button = tk.Button(root, text='发送', command=send)
send_button.pack(side=tk.LEFT)
input_box.bind('<Return>', send)

# 连接到服务器的函数
def connect_to_server():
    global client
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((SERVER_HOST, SERVER_PORT))
        
        # 启动接收线程
        receive_thread = threading.Thread(target=receive, daemon=True)
        receive_thread.start()
        
        # 在聊天框显示连接成功信息
        chat_box.config(state='normal')
        chat_box.insert(tk.END, f"已连接到服务器！昵称：{nickname}\n", 'system')
        chat_box.config(state='disabled')
        
    except Exception as e:
        messagebox.showerror("连接错误", f"无法连接到服务器: {e}")
        root.quit()

# 配置系统消息样式
chat_box.tag_config('system', foreground='blue')

# 连接到服务器
root.after(100, connect_to_server)  # 延迟连接，确保GUI完全初始化

# 运行GUI主循环
root.mainloop()
