"""
ROS Topic查看器 - 主应用入口
采用函数式编程风格，简洁的UI设计
"""
import logging
from nicegui import ui
from ros_config import ROSManager
from ui_simple import create_simple_ui, update_ui_status, refresh_topic_list

# 配置日志
logging.basicConfig(level=logging.INFO)

# 创建ROS管理器
ros_manager = ROSManager()

# 全局UI状态
ui_state = None

# 设置 ROS 管理器的通知回调
ros_manager.set_notify_callback(lambda msg, type='info': ui.notify(msg, type=type))


# ==================== 连接管理函数 ====================

def on_connect(host: str, port: int):
    """连接到ROS
    
    Args:
        host: 主机地址
        port: 端口号
    """
    global ui_state
    
    if ros_manager.connect(host, port):
        # 连接成功后更新UI状态
        if ui_state:
            update_ui_status(ui_state, ros_manager)
            # 自动刷新topic列表
            refresh_topic_list(ui_state, ros_manager)


def on_disconnect():
    """断开ROS连接"""
    global ui_state
    
    ros_manager.disconnect()
    
    # 更新UI状态
    if ui_state:
        update_ui_status(ui_state, ros_manager)


# ==================== 主应用设置函数 ====================

def setup_application():
    """设置应用程序
    
    Returns:
        Dict: UI状态字典
    """
    global ui_state
    
    # 创建简单UI
    ui_state = create_simple_ui(ros_manager, on_connect, on_disconnect)
    
    return ui_state


# ==================== 应用启动 ====================

if __name__ == "__main__":
    # 设置应用
    setup_application()
    
    # 运行应用
    ui.run(
        title="ROS Topic查看器",
        dark=False,
        reload=False,
        port=8080,
        show=False
    )
