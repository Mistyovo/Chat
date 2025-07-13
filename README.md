# 聊天室与文件传输系统

## 快速开始

### 开发者使用
1. **配置服务端**：首次运行会生成配置文件 `server_config.json`
2. **运行服务端**：`python server.py`
3. **运行客户端**：`python client.py`
4. **打包客户端**：`pyinstaller --onefile --windowed --name=ChatClient client.py`
5. **打包服务端**：`pyinstaller --onefile --console --name=ChatServer server.py`

### 最终用户使用
1. **获取程序**：从开发者处获取打包后的可执行文件（客户端和/或服务端）
2. **启动服务器**：双击 `ChatServer.exe` 或在命令行运行
3. **启动客户端**：双击 `ChatClient.exe`
4. **连接服务器**：在连接对话框中输入服务器信息即可使用

## 项目简介
本项目是一个基于 Python 和 Tkinter 的局域网聊天室与文件传输系统，包含客户端 (`client.py`) 和服务端 (`server.py`) 两部分。支持多用户实时聊天、文件上传与下载、密码认证、自动文件压缩等功能，适用于小型团队或局域网环境。

## 核心特性
- **实时聊天**：支持多用户文本消息交流，消息实时广播
- **文件传输**：支持文件上传/下载，自动gzip压缩传输
- **用户认证**：可选的密码认证机制，支持交互式密码设置
- **配置管理**：JSON格式配置文件，支持灵活的服务器配置
- **进度显示**：文件传输时显示详细进度信息
- **文件管理**：服务端维护文件元数据，支持文件列表浏览
- **错误处理**：完善的异常处理和用户提示机制

## 项目结构
```
├── client.py                # 客户端主程序（图形界面）
├── server.py                # 服务端主程序（命令行界面）
├── server_config.json       # 服务端配置文件（自动生成）
├── build_all.bat            # Windows一键打包脚本
├── build_all.sh             # Linux/macOS一键打包脚本
├── check_environment.bat    # Windows环境检查脚本
├── uploads/                 # 文件上传存储目录
│   └── file_metadata.json  # 文件元数据（自动生成）
├── dist/                    # 打包输出目录（打包后生成）
│   ├── ChatClient.exe       # 客户端可执行文件
│   └── ChatServer.exe       # 服务端可执行文件
├── README.md                # 项目说明文档
└── .venv/                   # Python虚拟环境（可选）
```

## 技术栈与依赖
- **Python版本**：3.7 及以上
- **核心库**：
  - `socket` - 网络通信
  - `threading` - 多线程处理
  - `tkinter` - GUI界面（客户端）
  - `gzip` - 文件压缩传输
  - `json` - 数据序列化和配置管理
- **标准库**：os, sys, time, datetime
- **无第三方依赖**：项目仅使用Python标准库，无需额外安装包

## 配置说明

### 服务端配置文件 (server_config.json)
首次运行服务端时会自动生成配置文件，包含以下配置项：

```json
{
    "server": {
        "host": "0.0.0.0",              // 监听地址，0.0.0.0表示监听所有网络接口
        "port": 55555,                  // 监听端口
        "password": "",                 // 服务器密码（空字符串表示无密码）
        "interactive_password_setup": true  // 是否启用交互式密码设置
    },
    "file_transfer": {
        "upload_dir": "uploads",        // 文件上传目录
        "buffer_size": 65536,           // 传输缓冲区大小（64KB）
        "max_file_size": 104857600      // 最大文件大小（100MB）
    },
    "logging": {
        "enable_logging": true,         // 是否启用日志
        "log_level": "INFO"            // 日志级别
    }
}
```

### 配置项详细说明
- **server.host**: 服务器监听地址
  - `0.0.0.0`: 监听所有网络接口（推荐）
  - `127.0.0.1`: 仅监听本地回环接口
  - 具体IP: 监听指定网络接口
- **server.port**: 服务器端口号（1-65535）
- **server.password**: 连接密码（为空则无需密码）
- **interactive_password_setup**: 启动时是否提示设置密码
- **file_transfer.upload_dir**: 文件存储目录路径
- **file_transfer.buffer_size**: 网络传输缓冲区大小
- **file_transfer.max_file_size**: 单个文件大小限制

## 安装与运行

### 环境准备
1. **安装Python**：确保系统已安装Python 3.7或更高版本
2. **克隆项目**：
   ```bash
   git clone <repository-url>
   cd Chat
   ```
3. **（可选）创建虚拟环境**：
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/macOS
   source .venv/bin/activate
   ```

### 启动服务端
1. **首次启动**：
   ```bash
   python server.py
   ```
   - 系统会自动创建配置文件 `server_config.json`
   - 如果启用了交互式密码设置，会提示输入密码
   - 服务端会创建 `uploads` 目录用于存储文件

2. **服务端启动信息示例**：
   ```
   ✅ Configuration file loaded successfully: server_config.json
   📋 Server Configuration:
      Listen Address: 0.0.0.0
      Listen Port: 55555
      Upload Directory: uploads
      Buffer Size: 65536
      Interactive Password Setup: Enabled
   📁 Created upload directory: uploads
   🚀 Server started successfully, listening on 0.0.0.0:55555
   Server password authentication: DISABLED
   ✅ Server is listening...
   ```

### 启动客户端
1. **运行客户端**：
   ```bash
   python client.py
   ```

2. **连接设置**：
   启动后会弹出连接对话框，需要填入：
   - **昵称**：在聊天室中显示的用户名
   - **服务器地址**：服务端IP地址（默认127.0.0.1）
   - **端口**：服务端监听端口（默认55555）
   - **密码**：如果服务端设置了密码则需要输入

3. **连接成功**：
   - 进入主界面，包含"聊天"和"文件传输"两个标签页
   - 可以开始发送消息和传输文件

## 程序打包部署

### 环境准备
在打包前，请确保已安装PyInstaller：
```bash
pip install pyinstaller
```

### 客户端打包

#### 打包命令
使用以下命令将客户端打包为独立可执行文件：
```bash
pyinstaller --onefile --windowed --name=ChatClient --clean --noconfirm client.py
```

#### 打包参数说明
- `--onefile`: 打包成单个exe文件，便于分发
- `--windowed`: 不显示控制台窗口，提供更好的用户体验
- `--name=ChatClient`: 设置生成的exe文件名
- `--clean`: 清理之前的构建缓存
- `--noconfirm`: 自动覆盖已存在的输出文件

#### 打包结果
打包成功后会生成：
- **主文件**: `dist/ChatClient.exe` (约8-15MB)
- **配置文件**: `ChatClient.spec` (可删除)
- **临时目录**: `build/` (可删除)

### 服务端打包

#### 打包命令
使用以下命令将服务端打包为独立可执行文件：
```bash
pyinstaller --onefile --console --name=ChatServer --clean --noconfirm server.py
```

#### 打包参数说明
- `--onefile`: 打包成单个exe文件，便于分发
- `--console`: 保留控制台窗口，用于显示服务器日志和状态信息
- `--name=ChatServer`: 设置生成的exe文件名
- `--clean`: 清理之前的构建缓存
- `--noconfirm`: 自动覆盖已存在的输出文件

#### 打包结果
打包成功后会生成：
- **主文件**: `dist/ChatServer.exe` (约6-12MB)
- **配置文件**: `ChatServer.spec` (可删除)
- **临时目录**: `build/` (可删除)

### 一键打包脚本

#### Windows批处理脚本 (build_all.bat)
```batch
@echo off
echo Building Chat Client and Server...

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo Installing/Upgrading PyInstaller...
pip install --upgrade pyinstaller

echo Building Client...
python -m PyInstaller --onefile --windowed --name=ChatClient --clean --noconfirm client.py

echo Building Server...
python -m PyInstaller --onefile --console --name=ChatServer --clean --noconfirm server.py

echo Build completed successfully!
pause
```

#### Linux/macOS脚本 (build_all.sh)
```bash
#!/bin/bash
echo "Building Chat Client and Server..."

# Check Python installation
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "Error: Python is not installed"
    exit 1
fi

PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "Installing/Upgrading PyInstaller..."
$PYTHON_CMD -m pip install --upgrade pyinstaller

echo "Building Client..."
$PYTHON_CMD -m PyInstaller --onefile --windowed --name=ChatClient --clean --noconfirm client.py

echo "Building Server..."
$PYTHON_CMD -m PyInstaller --onefile --console --name=ChatServer --clean --noconfirm server.py

echo "Build completed successfully!"
```

#### 使用说明
1. **环境检查**: 先运行 `check_environment.bat` 检查环境是否正确配置
2. **Windows用户**: 双击 `build_all.bat` 运行
3. **Linux/macOS用户**: 
   ```bash
   chmod +x build_all.sh
   ./build_all.sh
   ```
4. **常见问题**: 
   - 如果遇到权限错误，Windows用户请以管理员身份运行
   - Linux/macOS用户可能需要使用 `sudo` 来安装PyInstaller

### 分发部署

#### 客户端分发
1. **分发文件**: 只需分发 `dist/ChatClient.exe` 文件
2. **用户使用**: 双击exe文件即可运行，无需安装Python
3. **系统要求**: Windows 7及以上版本
4. **网络要求**: 需要网络连接到服务器

#### 服务端部署
1. **分发文件**: 分发 `dist/ChatServer.exe` 文件
2. **配置文件**: 首次运行会自动生成 `server_config.json`
3. **运行方式**: 
   - 双击exe文件启动（保持控制台窗口打开）
   - 或在命令行中运行以查看详细日志
4. **系统要求**: Windows Server 2008及以上版本或Windows 7及以上版本
5. **网络要求**: 需要开放指定端口（默认55555）

#### 完整部署包结构
```
ChatRoom_v1.0/
├── ChatClient.exe      # 客户端程序
├── ChatServer.exe      # 服务端程序
├── README.txt          # 使用说明
└── server_config.json  # 服务端配置文件模板（可选）
```

## 使用指南

### 服务端操作

#### 启动服务

**方式一：运行源代码（开发模式）**
```bash
python server.py
```

**方式二：运行打包版本（生产环境推荐）**
- Windows: 双击 `ChatServer.exe` 或在命令行运行
- Linux/macOS: 在终端运行 `./ChatServer`

2. **配置修改**：
   - 修改 `server_config.json` 中的配置项
   - 重启服务器使配置生效

3. **密码设置**：
   - 如果启用交互式密码设置，启动时会提示输入密码
   - 也可以直接在配置文件中设置 `server.password` 字段

4. **文件管理**：
   - 上传的文件存储在 `uploads` 目录
   - 文件元数据保存在 `uploads/file_metadata.json`
   - 服务端会自动同步文件和元数据

### 客户端操作

#### 连接设置
启动客户端后在连接对话框中输入：
- **昵称**: 您在聊天室中的显示名称
- **服务器地址**: 服务器IP地址（默认127.0.0.1）
- **端口**: 服务器端口（默认55555）
- **密码**: 服务器密码（如果服务端设置了密码）

#### 聊天功能
- 在聊天界面的输入框中输入消息
- 按回车键或点击"发送"按钮发送消息
- 消息会实时广播给所有在线用户
- 用户加入/离开聊天室会显示系统通知

#### 文件传输功能
**上传文件**：
1. 切换到"文件传输"标签页
2. 点击"选择文件上传"按钮
3. 选择要上传的文件（最大100MB）
4. 文件会自动压缩并上传到服务器
5. 上传完成后会显示进度和压缩信息

**下载文件**：
1. 在文件列表中查看可下载的文件
2. 双击文件或选中后点击"下载选中文件"
3. 选择保存位置
4. 文件会自动下载并解压缩
5. 下载完成后显示文件信息

**刷新文件列表**：
- 点击"刷新文件列表"按钮获取最新的文件信息
   ```bash
   python server.py
   ```
2. 首次启动可设置服务器密码（可为空，允许任何人连接）。
3. 服务端监听端口（默认 55555），等待客户端连接。

### 客户端启动

#### 方式一：运行源代码（开发模式）
1. 确保已安装Python 3.7+
2. 运行客户端：
   ```bash
   python client.py
   ```

#### 方式二：运行打包版本（推荐给最终用户）
1. 双击 `dist/ChatClient.exe` 启动程序
2. 无需安装Python或任何依赖

#### 连接设置
无论使用哪种方式启动，都需要在连接对话框中输入：
- **昵称**: 您在聊天室中的显示名称
- **服务器地址**: 服务器IP地址（默认127.0.0.1）
- **端口**: 服务器端口（默认55555）
- **密码**: 服务器密码（如果服务端设置了密码）

连接成功后进入主界面，可进行聊天和文件操作。

### 文件上传
- 点击“选择文件上传”，选择本地文件。
- 文件大小限制为 100MB，超出将提示错误。
- 上传完成后，其他用户可见并下载。

### 文件下载
- 在“可下载文件”列表中双击或选中后点击“下载选中文件”。
- 选择保存路径，下载进度实时显示。

## 主要架构说明
### 服务端
- 多线程处理每个客户端连接。
- 采用长度前缀协议传输密码和文件元数据，确保数据完整性。
- 文件上传时自动生成唯一文件名，避免冲突。
- 文件列表和元数据自动同步，清理无效记录。

### 客户端
- 基于 Tkinter 实现图形界面，支持聊天和文件操作分栏。
- 通过 socket 与服务端通信，异步接收消息。
- 文件上传/下载均采用 gzip 压缩，提升效率。
- 进度窗口实时反馈操作状态。

## 注意事项
- 请确保客户端和服务端 Python 版本兼容。
- 文件传输采用内存压缩，超大文件可能导致内存占用较高。
- 服务端上传目录和元数据文件需有写权限。
- 局域网环境下建议关闭防火墙或开放指定端口。

## 常见问题与疑难解答

### 环境问题
- **Python未安装或未加入PATH**：
  - 下载并安装Python 3.7+，安装时勾选"Add Python to PATH"
  - 或手动将Python安装目录添加到系统PATH环境变量

- **pip命令不可用**：
  - 确保pip已安装：`python -m ensurepip --upgrade`
  - 或重新安装Python并确保包含pip

### 打包问题
- **'pyinstaller' is not recognized**：
  - 使用 `python -m PyInstaller` 代替 `pyinstaller`
  - 或确保PyInstaller安装目录在PATH中

- **PyInstaller安装失败**：
  - 尝试升级pip：`python -m pip install --upgrade pip`
  - 使用镜像源：`pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pyinstaller`

- **权限不足错误**：
  - Windows：以管理员身份运行命令提示符
  - Linux/macOS：使用 `sudo` 命令

- **打包后程序无法运行**：
  - 检查是否缺少依赖模块，使用 `--hidden-import` 参数
  - 确保没有使用相对路径引用外部文件

### 连接问题
- **客户端无法连接服务器**：
  - 检查服务器IP地址和端口是否正确
  - 确保服务器程序正在运行
  - 检查防火墙设置，开放相应端口

- **认证失败**：
  - 确认服务器密码设置是否正确
  - 检查客户端输入的密码是否与服务器一致

### 文件传输问题
- **文件上传/下载失败**：
  - 检查文件大小是否超过100MB限制
  - 确保网络连接稳定
  - 检查服务器磁盘空间是否充足

- **文件损坏或无法打开**：
  - 重新下载文件
  - 检查传输过程中是否有网络中断

### 性能问题
- **程序运行缓慢**：
  - 首次启动打包版本较慢是正常现象
  - 大文件传输时会占用较多内存和CPU
  - 考虑在配置文件中调整缓冲区大小

## 贡献与扩展
欢迎根据实际需求扩展功能，如：

### 功能增强
- 增加文件类型过滤、断点续传、消息加密等
- 支持群组聊天、私聊功能
- 添加表情包、图片预览等

### 用户体验优化
- 优化界面交互体验
- 添加主题切换、字体设置
- 支持消息历史记录

### 部署扩展
- 支持Linux/macOS打包
- Docker容器化部署
- 提供安装包制作

### 开发相关
- 单元测试覆盖
- 代码文档完善
- 性能优化和内存管理

---
如有问题或建议，请联系开发者。
