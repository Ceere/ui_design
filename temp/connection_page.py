"""
连接页面 - 主页面显示ROS bridge连接需要的参数，及欢迎语，并且提供topic接口
"""
from nicegui import ui
from typing import Dict, Callable
from temp.ros_connection_manager import ROSManager


def create_connection_page(ros_manager: ROSManager, on_navigate_to_topic: Callable) -> Dict:
    """创建连接页面
    
    Args:
        ros_manager: ROS管理器实例
        on_navigate_to_topic: 导航到Topic页面的回调函数
        
    Returns:
        Dict: 页面状态字典
    """
    # 页面状态
    page_state = {
        'host_input': None,
        'port_input': None,
        'connection_status': None,
        'topic_input': None,
        'msg_type_input': None,
        'topics_container': None
    }
    
    # 欢迎语和介绍
    with ui.card().classes("w-full mb-6"):
        ui.label("欢迎使用ROS Topic查看器").classes("text-2xl font-bold text-blue-600 mb-2")
        ui.label("这是一个基于ROS和NiceGUI的实时数据查看工具").classes("text-gray-600 mb-1")
        ui.label("• 连接ROS Bridge并管理Topic订阅").classes("text-gray-600 mb-1")
        ui.label("• 实时显示图像和文本数据").classes("text-gray-600 mb-1")
        ui.label("• 只保留最新一帧数据，确保实时性").classes("text-gray-600")
    
    # 两列布局
    with ui.row().classes("w-full gap-6"):
        # 左侧：连接配置
        with ui.column().classes("w-1/2"):
            create_connection_section(page_state, ros_manager, on_navigate_to_topic)
        
        # 右侧：Topic管理
        with ui.column().classes("w-1/2"):
            create_topic_management_section(page_state, ros_manager)
    
    return page_state


def create_connection_section(page_state: Dict, ros_manager: ROSManager, on_navigate_to_topic: Callable):
    """创建连接配置部分
    
    Args:
        page_state: 页面状态字典
        ros_manager: ROS管理器实例
        on_navigate_to_topic: 导航到Topic页面的回调函数
    """
    with ui.card().classes("w-full mb-4"):
        ui.label("ROS Bridge连接配置").classes("text-xl font-bold mb-4")
        
        # 连接参数输入
        with ui.row().classes("items-center gap-2 mb-3"):
            page_state['host_input'] = ui.input(
                "ROS主机地址",
                value="localhost",
                placeholder="例如: localhost 或 192.168.1.100"
            ).classes("w-48")
            
            page_state['port_input'] = ui.number(
                "ROS端口",
                value=9090,
                min=1,
                max=65535
            ).classes("w-32")
        
        # 连接按钮
        with ui.row().classes("gap-2 mb-4"):
            ui.button("连接ROS", 
                     on_click=lambda: on_connect_click(page_state, ros_manager),
                     color="green").classes("px-6")
            
            ui.button("断开连接", 
                     on_click=lambda: on_disconnect_click(ros_manager),
                     color="red").classes("px-6")
        
        # 连接状态显示
        with ui.row().classes("items-center gap-2"):
            status_dot = ui.icon("circle").classes("text-red-500 text-xl")
            page_state['connection_status'] = ui.label("未连接").classes("text-gray-600")
        
        # 导航到Topic页面按钮
        ui.separator().classes("my-4")
        ui.button("前往Topic页面 →", 
                 on_click=on_navigate_to_topic,
                 color="blue").classes("w-full py-3").props("disabled" if not ros_manager.is_connected else "")


def create_topic_management_section(page_state: Dict, ros_manager: ROSManager):
    """创建Topic管理部分
    
    Args:
        page_state: 页面状态字典
        ros_manager: ROS管理器实例
    """
    with ui.card().classes("w-full"):
        ui.label("Topic接口管理").classes("text-xl font-bold mb-4")
        
        # 添加新Topic
        with ui.row().classes("items-center gap-2 mb-4"):
            page_state['topic_input'] = ui.input(
                "Topic名称",
                value="/image_raw",
                placeholder="例如: /camera/image_raw"
            ).classes("w-48")
            
            page_state['msg_type_input'] = ui.input(
                "消息类型",
                value="sensor_msgs/Image",
                placeholder="例如: sensor_msgs/Image"
            ).classes("w-48")
            
            ui.button("添加Topic", 
                     on_click=lambda: on_add_topic_click(page_state, ros_manager),
                     color="blue")
        
        # 已配置的Topic列表
        ui.label("已配置的Topics:").classes("text-lg font-semibold mb-2")
        
        page_state['topics_container'] = ui.column().classes("w-full")
        
        # 初始显示Topic列表
        update_topics_display(page_state, ros_manager)
        
        # 刷新按钮
        ui.button("刷新Topic列表", 
                 on_click=lambda: update_topics_display(page_state, ros_manager),
                 color="gray").classes("mt-4 w-full")


def update_topics_display(page_state: Dict, ros_manager: ROSManager):
    """更新Topic列表显示
    
    Args:
        page_state: 页面状态字典
        ros_manager: ROS管理器实例
    """
    container = page_state.get('topics_container')
    if not container:
        return
    
    container.clear()
    
    topic_list = ros_manager.get_topic_list()
    
    if not topic_list:
        with container:
            ui.label("暂无配置的Topic").classes("text-gray-500 italic")
        return
    
    for topic_name in topic_list:
        with container:
            create_topic_card(topic_name, ros_manager, page_state)


def create_topic_card(topic_name: str, ros_manager: ROSManager, page_state: Dict):
    """创建单个Topic卡片
    
    Args:
        topic_name: Topic名称
        ros_manager: ROS管理器实例
        page_state: 页面状态字典
    """
    config = ros_manager.topic_configs.get(topic_name, {})
    
    with ui.card().classes("w-full mb-2 p-3"):
        with ui.row().classes("items-center justify-between"):
            # Topic信息
            with ui.column().classes("gap-1"):
                ui.label(topic_name).classes("font-bold text-blue-700")
                with ui.row().classes("text-sm text-gray-600"):
                    ui.label(f"类型: {config.get('msg_type', '未知')}")
                    ui.label(f"消息数: {config.get('frame_count', 0)}").classes("ml-3")
            
            # 状态标签
            status = "✅ 已订阅" if config.get('subscribed') else "⏸️ 未订阅"
            ui.label(status).classes("text-sm font-medium")
        
        # 操作按钮
        with ui.row().classes("gap-1 mt-2"):
            if not config.get('subscribed'):
                ui.button("订阅", 
                         on_click=lambda tn=topic_name: on_subscribe_topic_click(tn, ros_manager, page_state),
                         color="green").classes("text-xs px-3")
            else:
                ui.button("取消订阅", 
                         on_click=lambda tn=topic_name: on_unsubscribe_topic_click(tn, ros_manager, page_state),
                         color="orange").classes("text-xs px-3")
            
            ui.button("删除", 
                     on_click=lambda tn=topic_name: on_remove_topic_click(tn, ros_manager, page_state),
                     color="red").classes("text-xs px-3")


# ==================== 事件处理函数 ====================

def on_connect_click(page_state: Dict, ros_manager: ROSManager):
    """连接按钮点击事件
    
    Args:
        page_state: 页面状态字典
        ros_manager: ROS管理器实例
    """
    host = page_state['host_input'].value
    port = int(page_state['port_input'].value)
    
    if ros_manager.connect(host, port):
        # 更新连接状态显示
        if page_state.get('connection_status'):
            page_state['connection_status'].set_text("已连接")
        
        # 更新状态点颜色
        status_dot = page_state.get('connection_status_dot')
        if status_dot:
            status_dot.classes("text-green-500 text-xl")
        
        # 自动刷新Topic列表
        update_topics_display(page_state, ros_manager)


def on_disconnect_click(ros_manager: ROSManager):
    """断开连接按钮点击事件
    
    Args:
        ros_manager: ROS管理器实例
    """
    ros_manager.disconnect()


def on_add_topic_click(page_state: Dict, ros_manager: ROSManager):
    """添加Topic按钮点击事件
    
    Args:
        page_state: 页面状态字典
        ros_manager: ROS管理器实例
    """
    topic_name = page_state['topic_input'].value.strip()
    msg_type = page_state['msg_type_input'].value.strip()
    
    if not topic_name:
        ui.notify("Topic名称不能为空", type='warning')
        return
    
    if ros_manager.add_topic(topic_name, msg_type):
        # 清空输入框
        page_state['topic_input'].value = ""
        page_state['msg_type_input'].value = ""
        
        # 更新显示
        update_topics_display(page_state, ros_manager)


def on_remove_topic_click(topic_name: str, ros_manager: ROSManager, page_state: Dict):
    """删除Topic按钮点击事件
    
    Args:
        topic_name: Topic名称
        ros_manager: ROS管理器实例
        page_state: 页面状态字典
    """
    if ros_manager.remove_topic(topic_name):
        update_topics_display(page_state, ros_manager)


def on_subscribe_topic_click(topic_name: str, ros_manager: ROSManager, page_state: Dict):
    """订阅Topic按钮点击事件
    
    Args:
        topic_name: Topic名称
        ros_manager: ROS管理器实例
        page_state: 页面状态字典
    """
    if ros_manager.subscribe_topic(topic_name):
        update_topics_display(page_state, ros_manager)


def on_unsubscribe_topic_click(topic_name: str, ros_manager: ROSManager, page_state: Dict):
    """取消订阅Topic按钮点击事件
    
    Args:
        topic_name: Topic名称
        ros_manager: ROS管理器实例
        page_state: 页面状态字典
    """
    if ros_manager.unsubscribe_topic(topic_name):
        update_topics_display(page_state, ros_manager)
