"""
ROS Topic查看器 - 主应用入口
采用函数式编程风格，简洁的UI设计
精简架构，仅保留ui和ros两个文件夹
"""
import logging
from nicegui import ui
from temp.ros_connection_manager import ROSManager
from ui.connection_page import create_connection_page
from temp.topic_page import create_topic_page

# 配置日志
logging.basicConfig(level=logging.INFO)

# 创建ROS管理器
ros_manager = ROSManager()

# 全局页面状态
current_page = "connection"
connection_page_state = None
topic_page_state = None


# ==================== 页面管理函数 ====================

def switch_to_topic_page():
    """切换到Topic页面"""
    global current_page, topic_page_state
    
    if not ros_manager.is_connected:
        ui.notify("❌ 请先连接ROS", type='warning')
        return
    
    current_page = "topic"
    
    # 清除当前页面内容
    content_container.clear()
    
    # 创建Topic页面
    with content_container:
        topic_page_state = create_topic_page(ros_manager, switch_to_connection_page)


def switch_to_connection_page():
    """切换到连接页面"""
    global current_page, connection_page_state
    
    current_page = "connection"
    
    # 清除当前页面内容
    content_container.clear()
    
    # 创建连接页面
    with content_container:
        connection_page_state = create_connection_page(ros_manager, switch_to_topic_page)


# ==================== 应用设置函数 ====================

def setup_application():
    """设置应用程序"""
    global content_container
    
    # 设置ROS管理器的通知回调
    ros_manager.set_notify_callback(lambda msg, type='info': ui.notify(msg, type=type))
    
    # 创建主布局
    with ui.header().classes("bg-blue-600 text-white p-4"):
        ui.label("ROS Topic查看器").classes("text-2xl font-bold")
        
        # 导航菜单
        with ui.row().classes("ml-auto gap-4"):
            ui.button("连接页面", 
                     on_click=switch_to_connection_page,
                     color="blue" if current_page == "connection" else "gray")
            ui.button("Topic页面", 
                     on_click=switch_to_topic_page,
                     color="blue" if current_page == "topic" else "gray")
    
    # 内容容器
    content_container = ui.column().classes("w-full h-full p-4")
    
    # 初始显示连接页面
    switch_to_connection_page()
    
    return content_container


# ==================== 应用启动 ====================

def create_app():
    """创建应用函数，用于ui.run(root=create_app)"""
    return setup_application()

# 注意：应用由 main.py 启动，此处不直接运行