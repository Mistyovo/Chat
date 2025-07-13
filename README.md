# 聊天室与文件传输系统

<div align="center">

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)

**一个基于Python的跨平台局域网聊天室与文件传输系统**

[功能特性](#核心特性) • [快速开始](#快速开始) • [使用指南](#使用指南) • [技术架构](#技术架构详解) • [贡献指南](#贡献指南)

</div>

---

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
├── 使用说明.txt             # 简化版使用说明（用于分发）
├── uploads/                 # 文件上传存储目录
│   └── file_metadata.json  # 文件元数据（自动生成）
├── dist/                    # 打包输出目录（打包后生成）
│   ├── ChatClient.exe       # 客户端可执行文件
│   └── ChatServer.exe       # 服务端可执行文件
├── README.md                # 项目完整文档
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

## 技术架构详解

### 服务端架构 (server.py)
- **多线程处理**：为每个客户端连接创建独立线程，支持并发处理多用户
- **配置管理**：JSON格式配置文件，支持热重载和默认配置自动生成
- **认证机制**：
  - 采用长度前缀协议传输密码，确保数据完整性
  - 支持交互式密码设置和配置文件密码设置
  - 密码验证失败自动断开连接，防止暴力破解
- **文件管理**：
  - 自动生成时间戳前缀的唯一文件名，避免文件名冲突
  - 维护完整的文件元数据JSON，记录上传者、时间、大小等信息
  - 文件与元数据自动同步，定期清理无效记录
- **网络通信**：
  - 基于Socket TCP协议，保证数据传输可靠性
  - 实现消息广播机制，支持实时聊天
  - 文件传输采用分块传输和gzip压缩，优化传输效率

### 客户端架构 (client.py)
- **图形界面**：
  - 基于Tkinter实现跨平台GUI，兼容Windows、Linux、macOS
  - 采用标签页布局设计：聊天界面 + 文件传输界面
  - 提供进度窗口和详细的状态提示信息
- **网络通信**：
  - 使用独立线程进行异步消息接收，不阻塞UI操作
  - 实现完整的协议解析和消息分类处理机制
  - 文件传输进度实时反馈，支持传输状态监控
- **文件处理**：
  - 自动gzip压缩/解压缩，平均节省30-80%传输带宽
  - 文件大小和类型检查，防止超大文件影响系统性能
  - 支持上传/下载进度显示和传输状态管理

### 通信协议设计
1. **认证协议**：
   ```
   Server -> Client: "NICK"
   Client -> Server: <nickname>
   Server -> Client: "PASS"
   Client -> Server: <password_length:4bytes><password_data>
   Server -> Client: "AUTH_SUCCESS" | "AUTH_FAILED"
   ```

2. **文件传输协议**：
   ```
   Upload: UPLOAD_FILE:<filename>:<compressed_size>:<compressed_data>
   Download: DOWNLOAD_FILE:<unique_filename>
   File List: GET_FILE_LIST -> FILE_LIST:<length>:<json_data>
   File Info: FILE_INFO:<length>:<json_metadata>
   ```

3. **消息协议**：
   ```
   Chat Message: <nickname>: <message_content>
   System Message: <system_notification>
   Status Message: UPLOAD_SUCCESS | DOWNLOAD_COMPLETE | etc.
   ```

### 安全性设计
- **数据传输**：密码使用长度前缀协议，避免截断攻击
- **文件安全**：唯一文件名生成，防止文件覆盖和路径遍历攻击
- **权限控制**：服务端文件访问限制在指定目录内
- **连接管理**：异常连接自动清理，防止资源泄露

### 性能优化
- **内存管理**：文件传输采用流式处理，避免大文件占用过多内存
- **网络优化**：gzip压缩减少网络传输量，分块传输支持大文件
- **并发处理**：多线程架构支持多用户同时操作
- **缓存机制**：文件元数据缓存，减少磁盘I/O操作

## 部署场景与最佳实践

### 局域网部署
**适用场景**：小型团队、办公室内部通信
- 服务器部署在局域网内的固定设备上
- 客户端通过内网IP连接，速度快且稳定
- 建议关闭服务器密码认证，简化使用流程

**部署步骤**：
1. 在局域网内选择一台稳定的设备作为服务器
2. 修改配置文件中的host为`0.0.0.0`
3. 确保防火墙开放相应端口
4. 将服务器IP告知所有用户

### 互联网部署
**适用场景**：远程团队、跨地域协作
- 服务器部署在公网服务器上
- 必须启用密码认证确保安全性
- 建议使用HTTPS代理或VPN隧道加强安全

**安全建议**：
1. 启用强密码认证
2. 定期更改服务器密码
3. 监控异常连接和文件上传
4. 定期备份uploads目录

### 容器化部署
**Docker部署示例**：
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY server.py .
COPY server_config.json .
EXPOSE 55555
CMD ["python", "server.py"]
```

## 扩展开发指南

### 自定义协议扩展
添加新的消息类型：
```python
# 在handle_single_message中添加新的消息处理
elif message.startswith("CUSTOM_COMMAND:"):
    handle_custom_command(message)
```

### 插件系统设计
通过配置文件加载插件：
```json
{
    "plugins": {
        "file_filter": "plugins/file_filter.py",
        "user_auth": "plugins/ldap_auth.py"
    }
}
```

### 数据库集成
将文件元数据存储到数据库：
```python
import sqlite3
# 替换JSON文件存储
def save_file_metadata_to_db(file_info):
    conn = sqlite3.connect('chat_files.db')
    # 插入文件信息到数据库
```

### API接口扩展
添加RESTful API支持：
```python
from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/api/files')
def get_files():
    return jsonify(uploaded_files)
```

## 版本信息

### 当前版本：v1.0.0
**发布日期**：2025年7月

**主要特性**：
- ✅ 多用户实时聊天
- ✅ 文件上传/下载（最大100MB）
- ✅ 自动文件压缩传输
- ✅ 密码认证机制
- ✅ 跨平台GUI界面
- ✅ 一键打包脚本
- ✅ 详细配置管理

### 更新日志

#### v1.0.0 (2025-07-13)
- 🎉 首次发布
- ✨ 实现基础聊天功能
- ✨ 添加文件传输功能
- ✨ 支持服务端配置文件
- ✨ 提供客户端和服务端打包脚本
- ✨ 完善错误处理和用户提示
- 📚 编写完整项目文档

#### 计划中的功能 (v1.1.0)
- 🔄 断点续传支持
- 🎨 界面主题切换
- 📝 聊天记录保存
- 🔍 文件搜索功能
- 🌐 多语言支持
- 🔐 消息加密传输

## 系统要求

### 开发环境
- **操作系统**：Windows 7+, Linux, macOS 10.12+
- **Python版本**：3.7, 3.8, 3.9, 3.10, 3.11
- **内存要求**：最低512MB，推荐1GB+
- **磁盘空间**：最低100MB，根据文件存储需求调整

### 运行环境（打包版本）
- **Windows**：Windows 7 SP1及以上版本
- **Linux**：大多数主流发行版（Ubuntu 18.04+, CentOS 7+等）
- **macOS**：macOS 10.12及以上版本
- **内存要求**：最低256MB，推荐512MB+
- **网络要求**：支持TCP连接的局域网或互联网环境

### 网络端口要求
- **默认端口**：55555 (可在配置文件中修改)
- **协议**：TCP
- **防火墙**：需要开放相应的入站和出站规则

## 许可证与版权

### 开源许可证
本项目采用 **MIT License** 开源许可证发布。

```
MIT License

Copyright (c) 2025 Chat Room Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### 第三方依赖
本项目仅使用Python标准库，无第三方依赖。所有功能均基于：
- `socket` - 网络通信（Python标准库）
- `threading` - 多线程处理（Python标准库）
- `tkinter` - GUI界面（Python标准库）
- `json` - 数据序列化（Python标准库）
- `gzip` - 数据压缩（Python标准库）

## 贡献指南

### 如何贡献
我们欢迎各种形式的贡献，包括但不限于：
- 🐛 报告Bug和问题
- 💡 提出新功能建议
- 📝 改进文档
- 🔧 提交代码修复
- 🌐 翻译和本地化

### 贡献流程
1. **Fork项目**：点击GitHub页面右上角的Fork按钮
2. **创建分支**：`git checkout -b feature/your-feature-name`
3. **开发功能**：进行您的修改和改进
4. **测试验证**：确保代码正常工作
5. **提交代码**：`git commit -m "Add your feature"`
6. **推送分支**：`git push origin feature/your-feature-name`
7. **创建PR**：在GitHub上创建Pull Request

### 代码规范
- 遵循PEP 8 Python代码风格
- 添加适当的注释和文档字符串
- 确保新功能有对应的测试
- 保持向后兼容性

### 问题报告
提交Issue时请包含：
- 操作系统和Python版本
- 详细的错误描述和重现步骤
- 相关的错误日志和截图
- 期望的行为描述

## 致谢

### 特别感谢
- 感谢所有贡献者的代码贡献和建议
- 感谢Python社区提供的优秀标准库
- 感谢开源社区的支持和反馈

### 参考项目
本项目在开发过程中参考了以下优秀项目：
- [Python Socket Programming](https://docs.python.org/3/library/socket.html)
- [Tkinter Documentation](https://docs.python.org/3/library/tkinter.html)
- [PyInstaller](https://pyinstaller.readthedocs.io/)

---

**最后更新时间**：2025年7月13日  
**文档版本**：v1.0.0  
**项目状态**：✅ 活跃开发中

> 💡 **提示**：如果这个项目对您有帮助，请给我们一个⭐Star支持！
