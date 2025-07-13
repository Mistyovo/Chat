import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import socket
import threading
import json
import gzip
import os
import time

BUFFER_SIZE = 65536 
MAX_FILE_SIZE = 100 * 1024 * 1024 
root = tk.Tk()
root.withdraw()



def get_connection_settings():
    temp_root = tk.Tk()
    temp_root.withdraw()
    dialog = tk.Toplevel(temp_root)
    dialog.title("连接设置")
    dialog.geometry("340x150")
    dialog.resizable(False, False)
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (340 // 2)
    y = (dialog.winfo_screenheight() // 2) - (150 // 2)
    dialog.geometry(f"340x150+{x}+{y}")
    dialog.lift()
    dialog.focus_force()
    dialog.attributes("-topmost", True)
    def remove_topmost():
        dialog.attributes("-topmost", False)
    dialog.after(100, remove_topmost)
    result = {}
    tk.Label(dialog, text="昵称:", font=("Arial", 10)).grid(row=0, column=0, sticky="w", padx=8, pady=8)
    nickname_entry = tk.Entry(dialog, width=25, font=("Arial", 10))
    nickname_entry.grid(row=0, column=1, columnspan=3, padx=8, pady=8, sticky="ew")
    nickname_entry.focus()
    tk.Label(dialog, text="服务器地址:", font=("Arial", 10)).grid(row=1, column=0, sticky="w", padx=8, pady=3)
    host_entry = tk.Entry(dialog, width=12, font=("Arial", 10))
    host_entry.insert(0, "127.0.0.1")
    host_entry.grid(row=1, column=1, padx=(8, 3), pady=3, sticky="ew")
    tk.Label(dialog, text="端口:", font=("Arial", 10)).grid(row=1, column=2, sticky="w", padx=3, pady=3)
    port_entry = tk.Entry(dialog, width=8, font=("Arial", 10))
    port_entry.insert(0, "55555")
    port_entry.grid(row=1, column=3, padx=(3, 8), pady=3)
    tk.Label(dialog, text="密码:", font=("Arial", 10)).grid(row=2, column=0, sticky="w", padx=8, pady=3)
    password_entry = tk.Entry(dialog, width=25, font=("Arial", 10), show="*")
    password_entry.grid(row=2, column=1, columnspan=3, padx=8, pady=3, sticky="ew")
    dialog.grid_columnconfigure(1, weight=1)
    button_frame = tk.Frame(dialog)
    button_frame.grid(row=3, column=0, columnspan=4, pady=10)
    def on_ok():
        nickname = nickname_entry.get().strip()
        host = host_entry.get().strip()
        port_str = port_entry.get().strip()
        password = password_entry.get()
        if not nickname:
            messagebox.showwarning("输入错误", "请输入昵称！")
            nickname_entry.focus()
            return
        if not host:
            messagebox.showwarning("输入错误", "请输入服务器地址！")
            host_entry.focus()
            return
        if not port_str:
            messagebox.showwarning("输入错误", "请输入端口号！")
            port_entry.focus()
            return
        try:
            port = int(port_str)
            if port < 1 or port > 65535:
                raise ValueError("端口号必须在1-65535之间")
        except ValueError as e:
            messagebox.showerror("端口格式错误", f"端口号格式不正确！\n{e}")
            port_entry.focus()
            port_entry.select_range(0, tk.END)
            return
        result["nickname"] = nickname
        result["host"] = host
        result["port"] = port
        result["password"] = password
        result["success"] = True
        dialog.destroy()
        temp_root.destroy()
    def on_cancel():
        result["success"] = False
        dialog.destroy()
        temp_root.destroy()
    ok_button = tk.Button(button_frame, text="连接", command=on_ok, width=10)
    ok_button.pack(side=tk.LEFT, padx=5)
    cancel_button = tk.Button(button_frame, text="取消", command=on_cancel, width=10)
    cancel_button.pack(side=tk.LEFT, padx=5)
    def on_enter(event):
        on_ok()
    nickname_entry.bind("<Return>", on_enter)
    host_entry.bind("<Return>", on_enter)
    port_entry.bind("<Return>", on_enter)
    password_entry.bind("<Return>", on_enter)
    def on_close():
        result["success"] = False
        dialog.destroy()
        temp_root.destroy()
    dialog.protocol("WM_DELETE_WINDOW", on_close)
    temp_root.wait_window(dialog)
    return result



root.update()
settings = get_connection_settings()
if not settings.get("success", False):
    root.destroy()
    exit()
nickname = settings["nickname"]
SERVER_HOST = settings["host"]
SERVER_PORT = settings["port"]
SERVER_PASSWORD = settings["password"]
root.deiconify()
root.title("聊天室")
root.geometry("800x600")
root.minsize(600, 400)
client = None
available_files = []
current_download = None
progress_window = None 
download_save_path = None 



def receive():
    global current_download, progress_window
    while True:
        try:
            raw_message = client.recv(1024).decode("utf-8")
            messages = []
            if "AUTH_SUCCESS" in raw_message:
                if raw_message == "AUTH_SUCCESS":
                    messages = ["AUTH_SUCCESS"]
                elif raw_message.startswith("AUTH_SUCCESS"):
                    remaining = raw_message[12:]
                    messages = ["AUTH_SUCCESS", remaining] if remaining else ["AUTH_SUCCESS"]
                else:
                    messages = [raw_message]
            else:
                messages = [raw_message]
            for message in messages:
                if not message.strip():
                    continue
                handle_single_message(message.strip())
        except ConnectionResetError:
            print("连接被服务器重置")
            messagebox.showerror("连接断开", "与服务器的连接已断开！")
            root.quit()
            break
        except ConnectionAbortedError:
            print("连接被中止")
            messagebox.showerror("连接中止", "与服务器的连接被中止！")
            root.quit()
            break
        except Exception as e:
            print(f"接收消息错误: {e}")
            messagebox.showerror("错误", f"与服务器通信时发生错误: {e}")
            root.quit()
            break



def handle_single_message(message):
    global current_download, progress_window
    if message == "NICK":
        client.send(nickname.encode("utf-8"))
    elif message == "PASS":
        if SERVER_PASSWORD:
            password_to_send = SERVER_PASSWORD
        else:
            password_to_send = ""
        
        password_bytes = password_to_send.encode("utf-8")
        password_length = len(password_bytes)
        client.send(f"{password_length:04d}".encode("utf-8"))
        if password_length > 0:
            client.send(password_bytes)
        time.sleep(0.1)
    elif message == "AUTH_SUCCESS":
        chat_box.config(state="normal")
        auth_info = "无密码" if not SERVER_PASSWORD else "已验证密码"
        chat_box.insert(
            tk.END,
            f"已成功连接到服务器 {SERVER_HOST}:{SERVER_PORT} ({auth_info}) 昵称：{nickname}\n",
            "system",
        )
        chat_box.see(tk.END)
        chat_box.config(state="disabled")
        root.after(1000, refresh_file_list)
    elif message == "AUTH_FAILED":
        messagebox.showerror("认证失败", "服务器密码验证失败！请检查密码是否正确。")
        try:
            client.close()
        except:
            pass
        root.quit()
        return
    elif message.startswith("FILE_LIST:"):
        handle_file_list_message(message)
    elif message.startswith("FILE_INFO:"):
        handle_file_info_message(message)
    elif message.startswith("FILE_DATA_START:"):
        handle_file_data_start(message)
    elif message == "UPLOAD_SUCCESS":
        close_progress_window()
        messagebox.showinfo("上传成功", "文件上传成功！")
        notebook.select(1) 
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
        chat_box.config(state="normal")
        parts = message.split(": ", 1)
        if len(parts) > 1:
            username, text = parts
            chat_box.insert(tk.END, username, "username")
            chat_box.insert(tk.END, ": " + text + "\n")
        else:
            chat_box.insert(tk.END, message + "\n")
        chat_box.see(tk.END) 
        chat_box.config(state="disabled")



def handle_file_list_message(message):
    try:
        parts = message.split(":", 2)
        if len(parts) >= 3:
            data_length = int(parts[1])
            json_data = parts[2]
            while len(json_data.encode("utf-8")) < data_length:
                more_data = client.recv(
                    min(1024, data_length - len(json_data.encode("utf-8")))
                ).decode("utf-8")
                json_data += more_data
            file_list_data = json.loads(json_data)
            update_file_list(file_list_data["files"])
    except Exception as e:
        print(f"处理文件列表错误: {e}")



def handle_file_info_message(message):
    """处理文件信息消息"""
    global current_download
    try:
        parts = message.split(":", 2)
        if len(parts) >= 3:
            data_length = int(parts[1])
            json_data = client.recv(data_length).decode("utf-8")
            file_info = json.loads(json_data)
            current_download = file_info
            start_download_progress(file_info)
            client.send("READY".encode("utf-8"))
    except Exception as e:
        print(f"处理文件信息错误: {e}")



def handle_file_data_start(message):
    global current_download
    try:
        if not current_download:
            return
        file_size = int(message.split(":")[1])
        compressed_data = b""
        bytes_received = 0
        while bytes_received < file_size:
            chunk_size = min(BUFFER_SIZE, file_size - bytes_received)
            chunk = client.recv(chunk_size)
            if not chunk:
                break
            compressed_data += chunk
            bytes_received += len(chunk)
            progress = int((bytes_received / file_size) * 100)
            update_progress("下载中", progress)
        save_received_file(compressed_data)
    except Exception as e:
        print(f"处理文件数据错误: {e}")
        close_progress_window()
        messagebox.showerror("下载错误", f"文件下载失败: {e}")



def send(event=None):
    message = input_box.get()
    if message.strip():
        input_box.delete(0, tk.END)
        full_message = f"{nickname}: {message}"
        client.send(full_message.encode("utf-8"))



notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
chat_frame = tk.Frame(notebook)
notebook.add(chat_frame, text="聊天")
chat_box = tk.Text(chat_frame, state="disabled", height=15)
chat_box.tag_config("username", foreground="green")
chat_box.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
input_frame = tk.Frame(chat_frame)
input_frame.pack(fill=tk.X, padx=5, pady=5)
input_box = tk.Entry(input_frame)
input_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
send_button = tk.Button(input_frame, text="发送", command=send)
send_button.pack(side=tk.LEFT)
input_box.bind("<Return>", send)
file_transfer_frame = tk.Frame(notebook)
notebook.add(file_transfer_frame, text="文件传输")
main_file_frame = tk.Frame(file_transfer_frame)
main_file_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
left_frame = tk.Frame(main_file_frame)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
list_header_frame = tk.Frame(left_frame)
list_header_frame.pack(fill=tk.X, pady=(0, 5))
file_list_title = tk.Label(list_header_frame, text="可下载文件", font=("Arial", 10, "bold"))
file_list_title.pack(side=tk.LEFT)
file_count_label = tk.Label(list_header_frame, text="文件数量: 0", font=("Arial", 9), fg="gray")
file_count_label.pack(side=tk.RIGHT)
listbox_frame = tk.Frame(left_frame)
listbox_frame.pack(fill=tk.BOTH, expand=True)
file_listbox = tk.Listbox(listbox_frame, font=("Consolas", 9), selectmode=tk.SINGLE)
scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=file_listbox.yview)
file_listbox.config(yscrollcommand=scrollbar.set)
file_listbox.bind("<Double-1>", lambda event: download_file())
file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
right_frame = tk.Frame(main_file_frame)
right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
upload_button = tk.Button(right_frame, text="选择文件上传", command=lambda: upload_file())
upload_button.pack(fill=tk.X, pady=(0, 10))
refresh_button = tk.Button(right_frame, text="刷新文件列表", command=lambda: refresh_file_list())
refresh_button.pack(fill=tk.X, pady=(0, 10))
download_button = tk.Button(right_frame, text="下载选中文件", command=lambda: download_file())
download_button.pack(fill=tk.X)



def connect_to_server():
    global client
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(10)
        client.connect((SERVER_HOST, SERVER_PORT))
        client.settimeout(None)
        receive_thread = threading.Thread(target=receive, daemon=True)
        receive_thread.start()
    except socket.timeout:
        messagebox.showerror("连接超时", f"连接到服务器 {SERVER_HOST}:{SERVER_PORT} 超时！\n请检查服务器是否正在运行。")
        root.quit()
    except ConnectionRefusedError:
        messagebox.showerror("连接被拒绝", f"无法连接到服务器 {SERVER_HOST}:{SERVER_PORT}！\n请检查服务器地址和端口是否正确。")
        root.quit()
    except Exception as e:
        messagebox.showerror("连接错误", f"无法连接到服务器: {e}")
        root.quit()



chat_box.tag_config("system", foreground="blue")
root.after(100, connect_to_server)



def format_file_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"



def upload_file():
    try:
        file_path = filedialog.askopenfilename(
            title=f"选择要上传的文件 (最大 {MAX_FILE_SIZE // (1024*1024)} MB)",
            filetypes=[("所有文件", "*.*")],
        )
        if file_path:
            filename = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            if file_size > MAX_FILE_SIZE:
                messagebox.showerror(
                    "文件过大",
                    f"文件大小 {format_file_size(file_size)} 超过了最大限制 {format_file_size(MAX_FILE_SIZE)}！\n"
                    f"请选择更小的文件。",
                )
                return
            with open(file_path, "rb") as f:
                file_data = f.read()
            compressed_data = gzip.compress(file_data)
            compression_ratio = (1 - len(compressed_data) / len(file_data)) * 100
            show_progress_window("上传文件", filename)
            upload_message = f"UPLOAD_FILE:{filename}:{len(compressed_data)}:"
            client.send(upload_message.encode("utf-8"))
            bytes_sent = 0
            total_size = len(compressed_data)
            while bytes_sent < total_size:
                chunk_size = min(BUFFER_SIZE, total_size - bytes_sent)
                chunk = compressed_data[bytes_sent : bytes_sent + chunk_size]
                client.send(chunk)
                bytes_sent += chunk_size
                progress = int((bytes_sent / total_size) * 100)
                update_progress("上传中", progress)
                root.update_idletasks()
            update_progress("等待服务器确认", 100)
            chat_box.config(state="normal")
            chat_box.insert(
                tk.END,
                f"文件上传完成: {filename} (原始: {format_file_size(len(file_data))}, 压缩: {format_file_size(len(compressed_data))}, 压缩率: {compression_ratio:.1f}%)\n",
                "system",
            )
            chat_box.see(tk.END)
            chat_box.config(state="disabled")
    except Exception as e:
        close_progress_window()
        messagebox.showerror("上传错误", f"文件上传失败: {e}")



def refresh_file_list():
    try:
        client.send("GET_FILE_LIST".encode("utf-8"))
    except Exception as e:
        messagebox.showerror("刷新错误", f"刷新文件列表失败: {e}")



def update_file_list(files):
    global available_files
    available_files = files
    file_listbox.delete(0, tk.END)
    for file_info in files:
        size_str = format_file_size(file_info["size"])
        display_text = f"{file_info['filename']} - {file_info['uploader']} ({file_info['upload_time']}) [{size_str}]"
        file_listbox.insert(tk.END, display_text)
    file_count_label.config(text=f"文件数量: {len(files)}")



def download_file():
    global download_save_path
    try:
        selection = file_listbox.curselection()
        if not selection:
            messagebox.showwarning("选择文件", "请先选择要下载的文件")
            return
        selected_index = selection[0]
        if selected_index < len(available_files):
            file_info = available_files[selected_index]
            unique_filename = file_info["unique_filename"]
            original_filename = (
                unique_filename.split("_", 1)[-1]
                if "_" in unique_filename
                else unique_filename
            )
            download_save_path = filedialog.asksaveasfilename(
                title="选择下载保存位置",
                initialfile=original_filename,
                defaultextension="",
                filetypes=[("所有文件", "*.*")],
            )
            if not download_save_path:
                return 
            download_message = f"DOWNLOAD_FILE:{unique_filename}"
            client.send(download_message.encode("utf-8"))
            chat_box.config(state="normal")
            chat_box.insert(
                tk.END,
                f"正在下载文件: {file_info['filename']} 到 {download_save_path}\n",
                "system",
            )
            chat_box.see(tk.END)
            chat_box.config(state="disabled")
    except Exception as e:
        messagebox.showerror("下载错误", f"文件下载失败: {e}")
        download_save_path = None



def show_progress_window(title, filename):
    global progress_window
    progress_window = tk.Toplevel(root)
    progress_window.title(title)
    progress_window.geometry("400x150")
    progress_window.resizable(False, False)
    file_label = tk.Label(progress_window, text=f"文件: {filename}", font=("Arial", 10))
    file_label.pack(pady=10)
    progress_window.progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(
        progress_window, variable=progress_window.progress_var, maximum=100
    )
    progress_bar.pack(fill=tk.X, padx=20, pady=10)
    progress_window.progress_label = tk.Label(progress_window, text="0%")
    progress_window.progress_label.pack(pady=5)
    cancel_button = tk.Button(
        progress_window, text="取消", command=close_progress_window
    )
    cancel_button.pack(pady=10)
    progress_window.transient(root)
    progress_window.grab_set()



def update_progress(operation, progress):
    if progress_window:
        progress_window.progress_var.set(progress)
        progress_window.progress_label.config(text=f"{operation}: {progress}%")
        progress_window.update()



def close_progress_window():
    global progress_window
    if progress_window:
        progress_window.destroy()
        progress_window = None



def start_download_progress(file_info):
    show_progress_window("下载文件", file_info["filename"])



def save_received_file(compressed_data):
    global current_download, download_save_path
    try:
        if not current_download or not download_save_path:
            return
        file_data = gzip.decompress(compressed_data)
        with open(download_save_path, "wb") as f:
            f.write(file_data)
        close_progress_window()
        compression_ratio = (
            1 - current_download["compressed_size"] / current_download["size"]
        ) * 100
        messagebox.showinfo(
            "下载完成",
            f"文件已保存到: {download_save_path}\n"
            f"原始大小: {format_file_size(current_download['size'])}\n"
            f"压缩大小: {format_file_size(current_download['compressed_size'])}\n"
            f"压缩率: {compression_ratio:.1f}%",
        )
        chat_box.config(state="normal")
        chat_box.insert(
            tk.END, f"文件下载完成: {os.path.basename(download_save_path)}\n", "system"
        )
        chat_box.see(tk.END)
        chat_box.config(state="disabled")
        current_download = None
        download_save_path = None
    except Exception as e:
        close_progress_window()
        messagebox.showerror("保存错误", f"文件保存失败: {e}")
        current_download = None
        download_save_path = None



root.mainloop()
