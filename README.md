# Qualcomm Robotics SDK Tools - ROS Topic查看器

## 项目简介

基于ROS和NiceGUI的Topic数据查看器，专为Qualcomm Robotics SDK设计。支持ROS Topic订阅、SSH远程命令执行、实时数据可视化等功能。

## 主要功能

- **ROS Bridge连接管理**：连接/断开ROS Bridge，配置主机和端口
- **Topic数据查看**：订阅/取消订阅Topic，实时显示最新数据
- **SSH远程终端**：执行远程命令，保持工作目录状态
- **图像处理**：支持ROS Image消息的实时显示
- **双页面UI**：连接页面 + Topic页面，响应式设计

## 环境配置

### 1. 系统要求
- Python 3.8+
- Ubuntu 20.04+ (推荐) 或其他Linux发行版
- ROS 2 Humble 或更高版本 (可选，用于本地ROS环境)

### 2. Python环境配置

```bash
# 创建Python虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖包
pip install -r requirements.txt
```

### 3. 依赖包安装

如果没有requirements.txt文件，手动安装以下依赖：

```bash
# 核心依赖
pip install nicegui roslibpy paramiko

# 图像处理依赖
pip install opencv-python numpy pillow

# 开发工具
pip install black flake8 pytest
```

### 4. ROS环境配置（可选）

如果需要连接本地ROS环境：

```bash
# 安装ROS 2 (以Humble为例)
sudo apt update
sudo apt install ros-humble-desktop

# 设置ROS环境
source /opt/ros/humble/setup.bash

# 安装ROS Bridge
sudo apt install ros-humble-rosbridge-server

# 启动ROS Bridge
ros2 launch rosbridge_server rosbridge_websocket_launch.xml
```

## 使用方法

### 1. 启动应用

```bash
# 进入项目目录
cd /path/to/ui_design

# 激活虚拟环境
source venv/bin/activate

# 启动应用
python src/ui/main.py
```

应用将在 http://localhost:8080 启动。

### 2. 连接设备

1. **打开浏览器**访问 http://localhost:8080
2. **填写连接信息**：
   - Device IP: 设备IP地址 (如: 10.64.39.55)
   - Username: SSH用户名 (如: root)
   - Password: SSH密码
   - SSH Port: SSH端口 (默认: 22)
   - ROS Bridge Port: ROS桥接端口 (默认: 9090)
3. **点击Connect按钮**建立连接

### 3. 使用Topic页面

连接成功后自动跳转到Topic页面，或手动点击顶部导航栏的"Topic"链接。

#### 左侧边栏功能：

1. **设备状态**：
   - 显示当前IP地址
   - ROS Bridge连接状态和端口
   - SSH连接状态和端口
   - 最后更新时间

2. **ROS Topics**：
   - 点击"Select Topic"下拉按钮刷新Topic列表
   - 选择Topic进行订阅
   - 实时显示Topic名称和类型

3. **SSH Terminal**：
   - 输入SSH命令并执行
   - 支持cd命令保持工作目录
   - 显示命令执行结果
   - 支持回车键执行命令

#### 主内容区域：

- **Topic数据显示**：实时显示订阅的Topic数据
- **图像显示**：自动处理sensor_msgs/Image消息
- **文本显示**：显示std_msgs/String和其他消息类型

### 4. SSH命令执行示例

```bash
# 查看当前目录
pwd

# 切换目录并查看文件
cd /home
ls -la

# 查看系统信息
uname -a

# 查看进程
ps aux | grep ros

# 执行ROS命令
ros2 topic list
```

### 5. 常见操作

#### 重新连接设备
- 返回主页 (点击顶部导航栏的"Qualcomm Robotics SDK")
- 更新连接信息
- 点击Connect按钮

#### 刷新Topic列表
- 在Topic页面点击"Select Topic"下拉按钮
- 自动获取最新的Topic列表

#### 执行SSH命令
- 在SSH Terminal输入命令
- 点击"Execute Command"按钮或按回车键

## 项目结构

```
ui_design/
├── README.md                      # 项目说明文档
├── requirements.txt               # Python依赖包
├── src/
│   ├── device/                    # 设备管理模块
│   │   └── device.py              # 设备类
│   ├── ros/                       # ROS模块
│   │   ├── ros_bridge.py          # ROS Bridge连接管理
│   │   └── ros_topic.py           # ROS Topic管理
│   ├── ros_function/              # ROS功能模块
│   │   └── connect_ros_bridge.py  # ROS连接功能
│   ├── ssh/                       # SSH模块
│   │   └── ssh.py                 # SSH连接管理
│   ├── ui/                        # 用户界面
│   │   ├── main.py                # 主页面
│   │   ├── topic_page.py          # Topic页面
│   │   └── image_process.py       # 图像处理
│   └── ui_function/               # UI功能模块
│       ├── bridge_controller.py   # Bridge控制器
│       ├── connect_device_controller.py # 设备连接控制器
│       ├── topic_controller.py    # Topic控制器
│       └── get_object.py          # 对象获取工具
└── resource/                      # 资源文件
    └── *.jpg                      # 图片资源
```

## 故障排除

### 1. 连接失败
- 检查设备IP地址是否正确
- 确认SSH端口和ROS端口是否开放
- 验证用户名和密码
- 检查网络连接

### 2. Topic无法显示
- 确认ROS Bridge服务正在运行
- 检查Topic名称是否正确
- 确认消息类型是否支持

### 3. SSH命令执行失败
- 确认SSH连接状态
- 检查命令语法是否正确
- 确认用户权限

### 4. 应用启动失败
- 检查Python版本 (需要3.8+)
- 确认所有依赖包已安装
- 检查端口8080是否被占用

## 开发说明

### 代码规范
- 使用Black进行代码格式化
- 使用Flake8进行代码检查
- 遵循PEP 8编码规范

### 添加新功能
1. 在相应模块中添加新类或函数
2. 更新UI界面
3. 添加必要的测试
4. 更新文档

### 测试
```bash
# 运行单元测试
pytest tests/

# 检查代码规范
flake8 src/
```

## 许可证

MIT License

## 技术支持

如有问题或建议，请提交Issue或联系项目维护者。

---

**注意**：使用SSH功能时请确保有合法的访问权限，遵守相关法律法规。
