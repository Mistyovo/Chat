import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, ttk
import socket
import threading
import json
import base64
import gzip
import os

# 客户端配置
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 55555
BUFFER_SIZE = 65536  # 64KB缓冲区，提高传输速度

# 创建主窗口（用于弹出输入框）
root = tk.Tk()
root.withdraw()  # 先隐藏主窗口

# 弹出输入昵称对话框
nickname = simpledialog.askstring('昵称', '请输入你的昵称:')
if not nickname:
    exit()

root.deiconify()  # 显示主窗口
root.title('聊天室')
root.geometry('800x600')  # 设置窗口默认大小
root.minsize(600, 400)    # 设置最小窗口大小

# 初始化客户端变量
client = None
available_files = []  # 存储可下载的文件列表
current_download = None  # 当前下载信息
progress_window = None  # 进度窗口
download_save_path = None  # 用户选择的下载保存路径

# 接收服务器消息
def receive():
    global current_download, progress_window
    while True:
        try:
            # 接收服务器消息
            message = client.recv(1024).decode('utf-8')
            
            if message == 'NICK':
                client.send(nickname.encode('utf-8'))
            elif message.startswith("FILE_LIST:"):
                # 处理文件列表
                handle_file_list_message(message)
            elif message.startswith("FILE_INFO:"):
                # 处理文件下载信息
                handle_file_info_message(message)
            elif message.startswith("FILE_DATA_START:"):
                # 开始接收文件数据
                handle_file_data_start(message)
            elif message == "UPLOAD_SUCCESS":
                close_progress_window()
                messagebox.showinfo("上传成功", "文件上传成功！")
                # 自动切换到文件传输标签页并刷新文件列表
                notebook.select(1)  # 切换到文件传输标签页
                refresh_file_list()
            elif message == "UPLOAD_ERROR":
                close_progress_window()
                messagebox.showerror("上传失败", "文件上传失败！")
            elif message == "DOWNLOAD_ERROR":
                close_progress_window()
                messagebox.showerror("下载失败", "文件下载失败！")
            elif message == "FILE_NOT_FOUND":
                close_progress_window()
                messagebox.showerror("文件不存在", "要下载的文件不存在！")
            elif message == "DOWNLOAD_COMPLETE":
                close_progress_window()
                messagebox.showinfo("下载完成", "文件下载完成！")
            else:
                # 普通聊天消息
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
        except Exception as e:
            # 处理连接错误
            print(f"接收消息错误: {e}")
            messagebox.showerror("错误", "与服务器的连接已断开！")
            root.quit()
            break

def handle_file_list_message(message):
    """处理文件列表消息"""
    try:
        parts = message.split(":", 2)
        if len(parts) >= 3:
            data_length = int(parts[1])
            # 接收完整的JSON数据
            json_data = parts[2]
            while len(json_data.encode('utf-8')) < data_length:
                more_data = client.recv(min(1024, data_length - len(json_data.encode('utf-8')))).decode('utf-8')
                json_data += more_data
            
            file_list_data = json.loads(json_data)
            update_file_list(file_list_data['files'])
    except Exception as e:
        print(f"处理文件列表错误: {e}")

def handle_file_info_message(message):
    """处理文件信息消息"""
    global current_download
    try:
        parts = message.split(":", 2)
        if len(parts) >= 3:
            data_length = int(parts[1])
            # 接收JSON数据
            json_data = client.recv(data_length).decode('utf-8')
            
            file_info = json.loads(json_data)
            current_download = file_info
            start_download_progress(file_info)
            
            # 发送确认消息
            client.send("READY".encode('utf-8'))
    except Exception as e:
        print(f"处理文件信息错误: {e}")

def handle_file_data_start(message):
    """处理文件数据开始消息"""
    global current_download
    try:
        if not current_download:
            return
            
        file_size = int(message.split(":")[1])
        
        # 接收文件数据
        compressed_data = b""
        bytes_received = 0
        
        while bytes_received < file_size:
            chunk_size = min(BUFFER_SIZE, file_size - bytes_received)
            chunk = client.recv(chunk_size)
            if not chunk:
                break
            compressed_data += chunk
            bytes_received += len(chunk)
            
            # 更新进度
            progress = int((bytes_received / file_size) * 100)
            update_progress("下载中", progress)
        
        # 解压缩并保存文件
        save_received_file(compressed_data)
        
    except Exception as e:
        print(f"处理文件数据错误: {e}")
        close_progress_window()
        messagebox.showerror("下载错误", f"文件下载失败: {e}")


# 发送消息给服务器
def send(event=None):
    message = input_box.get()
    if message.strip():  # 只发送非空消息
        input_box.delete(0, tk.END)
        full_message = f'{nickname}: {message}'
        client.send(full_message.encode('utf-8'))

# 创建标签页控件
notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# 聊天标签页
chat_frame = tk.Frame(notebook)
notebook.add(chat_frame, text="聊天")

# 创建聊天框
chat_box = tk.Text(chat_frame, state='disabled', height=15)
chat_box.tag_config('username', foreground='green')
chat_box.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# 聊天输入区域
input_frame = tk.Frame(chat_frame)
input_frame.pack(fill=tk.X, padx=5, pady=5)

# 创建输入框
input_box = tk.Entry(input_frame)
input_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

# 创建发送按钮
send_button = tk.Button(input_frame, text='发送', command=send)
send_button.pack(side=tk.LEFT)
input_box.bind('<Return>', send)

# 文件传输标签页
file_transfer_frame = tk.Frame(notebook)
notebook.add(file_transfer_frame, text="文件传输")

# 创建主要的框架用于左右布局
main_file_frame = tk.Frame(file_transfer_frame)
main_file_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# 左侧文件列表区域
left_frame = tk.Frame(main_file_frame)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

# 文件列表标题和数量
list_header_frame = tk.Frame(left_frame)
list_header_frame.pack(fill=tk.X, pady=(0, 5))

file_list_title = tk.Label(list_header_frame, text="可下载文件", font=("Arial", 10, "bold"))
file_list_title.pack(side=tk.LEFT)

file_count_label = tk.Label(list_header_frame, text="文件数量: 0", font=("Arial", 9), fg="gray")
file_count_label.pack(side=tk.RIGHT)

# 文件列表框架
listbox_frame = tk.Frame(left_frame)
listbox_frame.pack(fill=tk.BOTH, expand=True)

# 文件列表和滚动条
file_listbox = tk.Listbox(listbox_frame, font=("Consolas", 9), selectmode=tk.SINGLE)
scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=file_listbox.yview)
file_listbox.config(yscrollcommand=scrollbar.set)

# 绑定双击事件
file_listbox.bind('<Double-1>', lambda event: download_file())

file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# 右侧操作按钮区域
right_frame = tk.Frame(main_file_frame)
right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))

# 文件上传按钮
upload_button = tk.Button(right_frame, text='选择文件上传', command=lambda: upload_file())
upload_button.pack(fill=tk.X, pady=(0, 10))

# 刷新按钮
refresh_button = tk.Button(right_frame, text='刷新文件列表', command=lambda: refresh_file_list())
refresh_button.pack(fill=tk.X, pady=(0, 10))

# 下载按钮
download_button = tk.Button(right_frame, text='下载选中文件', command=lambda: download_file())
download_button.pack(fill=tk.X)

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
        
        # 自动刷新文件列表
        root.after(1000, refresh_file_list)  # 延迟1秒后刷新文件列表
        
    except Exception as e:
        messagebox.showerror("连接错误", f"无法连接到服务器: {e}")
        root.quit()

# 配置系统消息样式
chat_box.tag_config('system', foreground='blue')

# 连接到服务器
root.after(100, connect_to_server)  # 延迟连接，确保GUI完全初始化

# 文件传输功能函数
def upload_file():
    """上传文件（修复版本）"""
    try:
        file_path = filedialog.askopenfilename(
            title="选择要上传的文件",
            filetypes=[("所有文件", "*.*")]
        )
        if file_path:
            filename = os.path.basename(file_path)
            
            # 读取并压缩文件
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            compressed_data = gzip.compress(file_data)
            compression_ratio = (1 - len(compressed_data) / len(file_data)) * 100
            
            # 显示进度窗口
            show_progress_window("上传文件", filename)
            
            # 发送文件上传请求
            upload_message = f"UPLOAD_FILE:{filename}:{len(compressed_data)}:"
            client.send(upload_message.encode('utf-8'))
            
            # 分块发送压缩数据
            bytes_sent = 0
            total_size = len(compressed_data)
            
            while bytes_sent < total_size:
                chunk_size = min(BUFFER_SIZE, total_size - bytes_sent)
                chunk = compressed_data[bytes_sent:bytes_sent + chunk_size]
                client.send(chunk)
                bytes_sent += chunk_size
                
                # 更新进度（客户端本地计算）
                progress = int((bytes_sent / total_size) * 100)
                update_progress("上传中", progress)
                
                # 短暂延迟，让进度条更新更平滑
                root.update_idletasks()
            
            # 上传完成，等待服务器确认
            update_progress("等待服务器确认", 100)
            
            # 在聊天框显示上传信息
            chat_box.config(state='normal')
            chat_box.insert(tk.END, 
                f"文件上传完成: {filename} (原始: {len(file_data)} 字节, 压缩: {len(compressed_data)} 字节, 压缩率: {compression_ratio:.1f}%)\n", 
                'system')
            chat_box.see(tk.END)
            chat_box.config(state='disabled')
            
    except Exception as e:
        close_progress_window()
        messagebox.showerror("上传错误", f"文件上传失败: {e}")

def refresh_file_list():
    """刷新文件列表"""
    try:
        client.send("GET_FILE_LIST".encode('utf-8'))
    except Exception as e:
        messagebox.showerror("刷新错误", f"刷新文件列表失败: {e}")

def update_file_list(files):
    """更新文件列表显示"""
    global available_files
    available_files = files
    file_listbox.delete(0, tk.END)
    
    for file_info in files:
        size_mb = file_info['size'] / (1024 * 1024)
        if size_mb < 1:
            size_str = f"{file_info['size']} B"
        else:
            size_str = f"{size_mb:.1f} MB"
        
        display_text = f"{file_info['filename']} - {file_info['uploader']} ({file_info['upload_time']}) [{size_str}]"
        file_listbox.insert(tk.END, display_text)
    
    # 更新文件数量标签
    file_count_label.config(text=f"文件数量: {len(files)}")

def download_file():
    """下载选中的文件"""
    global download_save_path
    try:
        selection = file_listbox.curselection()
        if not selection:
            messagebox.showwarning("选择文件", "请先选择要下载的文件")
            return
        
        selected_index = selection[0]
        if selected_index < len(available_files):
            file_info = available_files[selected_index]
            unique_filename = file_info['unique_filename']
            original_filename = unique_filename.split('_', 1)[-1] if '_' in unique_filename else unique_filename
            
            # 让用户选择保存位置
            download_save_path = filedialog.asksaveasfilename(
                title="选择下载保存位置",
                initialfile=original_filename,
                defaultextension="",
                filetypes=[("所有文件", "*.*")]
            )
            
            if not download_save_path:
                return  # 用户取消了保存
            
            # 发送下载请求
            download_message = f"DOWNLOAD_FILE:{unique_filename}"
            client.send(download_message.encode('utf-8'))
            
            # 在聊天框显示下载信息
            chat_box.config(state='normal')
            chat_box.insert(tk.END, f"正在下载文件: {file_info['filename']} 到 {download_save_path}\n", 'system')
            chat_box.see(tk.END)
            chat_box.config(state='disabled')
            
    except Exception as e:
        messagebox.showerror("下载错误", f"文件下载失败: {e}")
        download_save_path = None

def show_progress_window(title, filename):
    """显示进度窗口"""
    global progress_window
    progress_window = tk.Toplevel(root)
    progress_window.title(title)
    progress_window.geometry("400x150")
    progress_window.resizable(False, False)
    
    # 文件名标签
    file_label = tk.Label(progress_window, text=f"文件: {filename}", font=("Arial", 10))
    file_label.pack(pady=10)
    
    # 进度条
    progress_window.progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(progress_window, variable=progress_window.progress_var, maximum=100)
    progress_bar.pack(fill=tk.X, padx=20, pady=10)
    
    # 进度标签
    progress_window.progress_label = tk.Label(progress_window, text="0%")
    progress_window.progress_label.pack(pady=5)
    
    # 取消按钮
    cancel_button = tk.Button(progress_window, text="取消", command=close_progress_window)
    cancel_button.pack(pady=10)
    
    progress_window.transient(root)
    progress_window.grab_set()

def update_progress(operation, progress):
    """更新进度"""
    if progress_window:
        progress_window.progress_var.set(progress)
        progress_window.progress_label.config(text=f"{operation}: {progress}%")
        progress_window.update()

def close_progress_window():
    """关闭进度窗口"""
    global progress_window
    if progress_window:
        progress_window.destroy()
        progress_window = None

def start_download_progress(file_info):
    """开始下载进度显示"""
    show_progress_window("下载文件", file_info['filename'])

def save_received_file(compressed_data):
    """保存接收到的文件"""
    global current_download, download_save_path
    try:
        if not current_download or not download_save_path:
            return
            
        # 解压缩文件数据
        file_data = gzip.decompress(compressed_data)
        
        # 直接保存到用户选择的位置
        with open(download_save_path, 'wb') as f:
            f.write(file_data)
        
        close_progress_window()
        
        compression_ratio = (1 - current_download['compressed_size'] / current_download['size']) * 100
        messagebox.showinfo("下载完成", 
            f"文件已保存到: {download_save_path}\n"
            f"原始大小: {current_download['size']} 字节\n"
            f"压缩大小: {current_download['compressed_size']} 字节\n"
            f"压缩率: {compression_ratio:.1f}%")
        
        # 在聊天框显示下载完成信息
        chat_box.config(state='normal')
        chat_box.insert(tk.END, f"文件下载完成: {os.path.basename(download_save_path)}\n", 'system')
        chat_box.see(tk.END)
        chat_box.config(state='disabled')
        
        # 重置变量
        current_download = None
        download_save_path = None
        
    except Exception as e:
        close_progress_window()
        messagebox.showerror("保存错误", f"文件保存失败: {e}")
        current_download = None
        download_save_path = None

# 运行GUI主循环
root.mainloop()
