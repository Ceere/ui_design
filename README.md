# ROS Topic查看器

## 简介

基于ROS和NiceGUI的Topic数据查看器，满足以下需求：

1. ROS Bridge类管理ROS连接
2. 基于ROS Bridge订阅/取消订阅Topic
3. 只保留最新一帧数据
4. NiceGUI显示最新数据
5. 双页面UI：连接页面 + Topic页面
6. Topic页面左右布局：左侧选择订阅，右侧数据展示

## 项目结构

```
ui_design/
├── src/main.py                    # 应用入口
├── src/ros/                       # ROS模块
│   ├── ros_bridge.py              # ROS Bridge连接
│   ├── ros_topic.py               # ROS Topic管理
│   └── ros_connection_manager.py  # ROS连接管理器
└── src/ui/                        # UI模块
    ├── main_app.py                # 主应用逻辑
    ├── connection_page.py         # 连接页面
    └── topic_page.py              # Topic页面
```

## 功能特点

- **ROS连接管理**：连接/断开ROS Bridge，配置主机端口
- **Topic管理**：添加/删除Topic，订阅/取消订阅
- **最新数据**：只保留最新一帧数据（queue_size=1）
- **双页面UI**：连接页面 + Topic页面
- **响应式设计**：适应不同屏幕尺寸
- **实时显示**：图像和文本数据实时更新

## 快速开始

```bash
# 安装依赖
pip install roslibpy nicegui

# 运行应用
python src/main.py

# 访问 http://localhost:8080
```

## 使用说明

1. **连接ROS**：输入ROS Bridge地址（默认localhost:9090），点击连接
2. **配置Topic**：在连接页面添加Topic名称和消息类型
3. **查看数据**：连接成功后进入Topic页面，选择Topic订阅查看数据

## 文件说明

- `src/main.py` - 应用入口
- `src/ros/` - ROS相关模块
- `src/ui/` - 用户界面模块

## 许可证

MIT License
