# ROS Topic查看器 - 代码结构说明

## 项目概述
这是一个基于ROS和NiceGUI的Topic查看器，采用混合编程范式：
- **ROS连接部分**：对象式编程，确保稳定性和唯一连接
- **UI界面部分**：函数式编程，提高可维护性和可测试性

## 文件结构说明

### 核心模块

#### 1. `source/image_receiver.py` - ROS基础连接模块
- **功能**：提供ROS桥接器和Topic订阅器的底层实现
- **编程范式**：对象式编程
- **主要类**：
  - `RosBridge`：管理ROS连接，支持连接/断开操作
  - `RosTopic`：管理单个Topic的订阅/取消订阅
- **依赖**：roslibpy

#### 2. `source/ros_config.py` - ROS管理器模块
- **功能**：高级ROS连接和Topic管理，单例模式确保唯一连接
- **编程范式**：对象式编程
- **主要类**：
  - `ROSManager`：单例管理器，协调所有ROS操作
  - **关键功能**：
    - 连接/断开ROS系统
    - Topic配置管理（添加/删除）
    - Topic订阅/取消订阅
    - 消息处理（图像和文字）
    - 回调函数注册
- **依赖**：`image_receiver.py`, `ros_services.py`, `text_message_handler.py`

#### 3. `source/ros_services.py` - ROS服务管理模块
- **功能**：ROS服务调用和管理
- **编程范式**：对象式编程 + 函数式UI
- **主要类**：
  - `ROSServiceClient`：单个ROS服务客户端
  - `ServiceManager`：服务管理器
- **函数**：
  - `create_service_request_ui`：创建服务请求UI（函数式）
- **支持的服务类型**：常见ROS服务类型预定义

#### 4. `source/text_message_handler.py` - 文字消息处理模块
- **功能**：处理ROS文字Topic消息
- **编程范式**：混合式（对象式核心 + 函数式UI）
- **主要类**：
  - `TextMessageProcessor`：文字消息处理器
  - `TextTopicManager`：文字Topic管理器
- **函数**：
  - `create_text_topic_ui`：创建文字Topic UI（函数式）
- **功能**：JSON解析、消息格式化、历史记录管理

### UI模块

#### 5. `source/ui_simple.py` - 简单UI模块（当前使用）
- **功能**：简洁的Topic选择和数据显示界面
- **编程范式**：纯函数式编程
- **设计特点**：
  - 左侧控制面板（1/3宽度）
  - 右侧数据显示面板（2/3宽度）
  - Topic下拉选择框，自动获取可用Topic
  - 根据Topic类型动态显示数据（图像/文字）
- **主要函数**：
  - `create_simple_ui`：创建完整UI
  - `create_topic_selection_panel`：Topic选择面板
  - `create_display_panel`：数据显示面板

#### 6. `source/ui_enhancements.py` - 增强UI模块（备用）
- **功能**：更复杂的UI界面，包含多个功能面板
- **编程范式**：函数式编程
- **注意**：当前未使用，保留作为备用

#### 7. `source/ui_config.py` - UI配置模块（备用）
- **功能**：基础UI配置功能
- **编程范式**：函数式编程
- **注意**：当前未使用，保留作为备用

### 应用入口

#### 8. `source/nice.py` - 主应用入口
- **功能**：应用启动和主循环
- **编程范式**：函数式编程
- **主要功能**：
  - 初始化所有管理器
  - 设置通知回调
  - 创建UI界面
  - 启动NiceGUI服务器

## 使用说明

### 启动应用
```bash
cd /home/ubuntu/ui_design
python3 source/nice.py
```

### 连接ROS
1. 确保ROS系统正在运行（或使用ROS桥接器）
2. 在UI中输入ROS主机和端口（默认localhost:9090）
3. 点击"连接"按钮

### 使用流程
1. **连接ROS**：输入正确的ROS主机和端口
2. **刷新Topic列表**：点击"刷新"按钮获取可用Topic
3. **选择Topic**：从下拉框中选择要查看的Topic
4. **订阅Topic**：点击"订阅"按钮开始接收数据
5. **查看数据**：右侧面板根据Topic类型显示数据
   - 图像Topic：显示实时图像
   - 文字Topic：显示格式化消息

### 错误处理
- **连接失败**：检查ROS系统是否运行，端口是否正确
- **无可用Topic**：确保ROS系统中有发布Topic
- **订阅失败**：检查Topic名称和类型是否正确

## 编程范式说明

### 对象式编程（ROS部分）
- **目的**：确保状态管理和资源控制的稳定性
- **应用**：ROS连接、Topic订阅、服务调用
- **优点**：封装性好，状态管理清晰，适合硬件交互

### 函数式编程（UI部分）
- **目的**：提高UI代码的可维护性和可测试性
- **应用**：所有UI组件创建和事件处理
- **优点**：无副作用，易于组合和测试，代码清晰

## 扩展开发

### 添加新功能
1. **新Topic类型支持**：在`ros_config.py`的`_process_message`方法中添加处理逻辑
2. **新UI组件**：在`ui_simple.py`中添加新的函数式组件
3. **新服务类型**：在`ros_services.py`的`COMMON_SERVICE_TYPES`和`create_service_request_ui`中添加

### 代码规范
1. **注释**：所有函数和类都有完整的docstring
2. **类型提示**：使用Python类型提示提高代码可读性
3. **错误处理**：所有可能失败的操作都有try-catch和用户反馈
4. **日志记录**：使用logging模块记录重要操作和错误

## 故障排除

### 常见问题
1. **ROS连接失败**：检查ROS桥接器是否运行在指定端口
2. **无图像显示**：确认Topic类型是否为`sensor_msgs/Image`
3. **UI不更新**：检查回调函数是否正确注册
4. **内存泄漏**：及时取消订阅不再需要的Topic

### 调试建议
1. 查看控制台日志输出
2. 使用ROS命令行工具检查Topic状态
3. 逐步测试各个功能模块
