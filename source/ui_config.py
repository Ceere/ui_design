"""
UI配置模块 - 函数式编程实现
提供基础的UI配置功能，采用纯函数式编程风格
"""
from nicegui import ui
from typing import Dict, Callable, Optional
from ros_config import ROSManager


# UI状态（使用字典而不是类） - 函数式编程的状态管理
ui_state = {
    'image_placeholders': {},  # topic_name -> ui.image element
    'message_placeholders': {},  # topic_name -> ui.label element
    'topic_inputs': {},  # topic_name -> (topic_name_input, msg_type_input)
    'host_input': None,
    'port_input': None,
}


def create_ros_connection_section(ros_manager: ROSManager):
    """创建ROS连接配置部分
    
    Args:
        ros_manager: ROS管理器实例
    """
    with ui.row().classes("items-center"):
        ui.label("ROS Bridge 连接").classes("text-xl font-bold")
    
    with ui.row().classes("items-center gap-2"):
        ui_state['host_input'] = ui.input(
            "ROS Bridge Host", 
            value="localhost"
        ).classes("w-40")
        
        ui_state['port_input'] = ui.number(
            "ROS Bridge Port", 
            value=9090
        ).classes("w-32")
    
    with ui.row().classes("gap-2"):
        ui.button("连接", on_click=lambda: on_connect_click(ros_manager))
        ui.button("断开", on_click=lambda: on_disconnect_click(ros_manager)).props("color=red")


def create_topic_management_section(ros_manager: ROSManager):
    """创建Topic管理部分
    
    Args:
        ros_manager: ROS管理器实例
        
    Returns:
        Callable: 更新topic显示的函数
    """
    ui.label("Topic 管理").classes("text-xl font-bold mt-4")
    
    # 添加新topic的输入区域
    with ui.row().classes("items-center gap-2"):
        new_topic_input = ui.input("新Topic名称", value="/image_raw").classes("w-40")
        new_msg_type_input = ui.input("消息类型", value="sensor_msgs/Image").classes("w-40")
        ui.button("添加Topic", on_click=lambda: on_add_topic_click(
            ros_manager, new_topic_input, new_msg_type_input
        ))
    
    # 现有topic列表
    ui.label("已配置的Topics:").classes("text-lg font-semibold mt-4")
    topics_container = ui.column().classes("w-full")
    
    # 更新topic列表显示的函数
    def update_topics_display():
        """更新topic列表显示"""
        topics_container.clear()
        for topic_name in ros_manager.get_topic_list():
            with topics_container:
                create_topic_ui(ros_manager, topic_name)
    
    # 初始显示
    update_topics_display()
    
    # 返回更新函数以便外部调用
    return update_topics_display


def create_topic_ui(ros_manager: ROSManager, topic_name: str):
    """创建单个topic的UI
    
    Args:
        ros_manager: ROS管理器实例
        topic_name: topic名称
    """
    # 获取update_topics_display函数（通过闭包）
    update_display_func = ui_state.get('update_topics_display')
    
    with ui.card().classes("w-full mb-2"):
        with ui.row().classes("items-center justify-between w-full"):
            ui.label(f"Topic: {topic_name}").classes("font-bold")
            
            with ui.row().classes("gap-1"):
                ui.button("订阅", on_click=lambda: on_subscribe_topic_click(ros_manager, topic_name))
                ui.button("取消订阅", 
                         on_click=lambda: on_unsubscribe_topic_click(ros_manager, topic_name)
                         ).props("color=red")
                ui.button("删除", 
                         on_click=lambda: on_remove_topic_click(ros_manager, topic_name, update_display_func)
                         ).props("color=negative")
        
        # Topic配置
        with ui.row().classes("items-center gap-2 mt-2"):
            # 获取topic配置
            topic_config = None
            if topic_name in ros_manager.topic_configs:
                topic_config = ros_manager.topic_configs[topic_name]
            
            if topic_config:
                topic_name_input = ui.input(
                    "Topic名称", 
                    value=topic_config['topic_name']
                ).classes("w-40")
                msg_type_input = ui.input(
                    "消息类型", 
                    value=topic_config['msg_type']
                ).classes("w-40")
                
                # 保存输入引用
                ui_state['topic_inputs'][topic_name] = (topic_name_input, msg_type_input)
                
                ui.button("更新配置", 
                         on_click=lambda: on_update_topic_click(
                             ros_manager, topic_name, topic_name_input, msg_type_input
                         ))
        
        # 消息显示区域
        with ui.row().classes("w-full mt-2"):
            # 图像显示（如果topic是图像类型）
            if topic_name not in ui_state['image_placeholders']:
                image_placeholder = ui.image("").classes("max-w-[200px] max-h-[200px] object-contain")
                image_placeholder.set_source("data:,")
                ui_state['image_placeholders'][topic_name] = image_placeholder
            
            # 消息文本显示
            if topic_name not in ui_state['message_placeholders']:
                message_placeholder = ui.label(f"等待 {topic_name} 消息...").classes("ml-4")
                ui_state['message_placeholders'][topic_name] = message_placeholder
            
            # 注册回调
            ros_manager.register_ui_callbacks(
                topic_name,
                image_callback=lambda img_base64: update_topic_image(topic_name, img_base64),
                message_callback=lambda msg: update_topic_message(topic_name, msg)
            )


def create_main_image_display():
    """创建主图像显示区域（显示选中的topic图像）
    
    Returns:
        ui.image: 主图像显示元素
    """
    ui.label("图像显示").classes("text-2xl font-bold mt-6")
    main_image = ui.image("").classes("max-w-[80%] max-h-[80%] object-contain border-2 rounded-lg")
    main_image.set_source("data:,")
    return main_image


def setup_ui(ros_manager: ROSManager):
    """配置完整的UI界面（函数式编程风格）
    
    Args:
        ros_manager: ROS管理器实例
    """
    with ui.header():
        ui.label("ROS2 多Topic实时图像流").classes("text-2xl font-bold")
    
    with ui.row().classes("w-full h-screen"):
        # 左侧配置面板
        with ui.column().classes("w-1/3 p-4 border-r-2 h-full overflow-y-auto"):
            create_ros_connection_section(ros_manager)
            update_topics_display = create_topic_management_section(ros_manager)
        
        # 右侧主显示区域
        with ui.column().classes("w-2/3 p-4 h-full overflow-y-auto"):
            main_image = create_main_image_display()
            ui_state['main_image'] = main_image
    
    # 保存更新函数到全局状态
    ui_state['update_topics_display'] = update_topics_display


# ==================== 事件处理函数 ====================

def on_connect_click(ros_manager: ROSManager):
    """连接按钮点击事件
    
    Args:
        ros_manager: ROS管理器实例
    """
    host = ui_state['host_input'].value
    port = int(ui_state['port_input'].value)
    ros_manager.connect(host, port)


def on_disconnect_click(ros_manager: ROSManager):
    """断开按钮点击事件
    
    Args:
        ros_manager: ROS管理器实例
    """
    ros_manager.disconnect()


def on_add_topic_click(ros_manager: ROSManager, topic_input, msg_type_input):
    """添加Topic按钮点击事件
    
    Args:
        ros_manager: ROS管理器实例
        topic_input: topic输入框
        msg_type_input: 消息类型输入框
    """
    topic_name = topic_input.value.strip()
    msg_type = msg_type_input.value.strip()
    
    if not topic_name:
        ui.notify("Topic名称不能为空", type='warning')
        return
    
    if ros_manager.add_topic(topic_name, msg_type):
        # 更新UI显示
        if 'update_topics_display' in ui_state:
            ui_state['update_topics_display']()
    else:
        ui.notify(f"Topic {topic_name} 已存在", type='warning')


def on_remove_topic_click(ros_manager: ROSManager, topic_name: str, update_display_func):
    """删除Topic按钮点击事件
    
    Args:
        ros_manager: ROS管理器实例
        topic_name: topic名称
        update_display_func: 更新显示的函数
    """
    if ros_manager.remove_topic(topic_name):
        # 清理UI元素
        if topic_name in ui_state['image_placeholders']:
            del ui_state['image_placeholders'][topic_name]
        if topic_name in ui_state['message_placeholders']:
            del ui_state['message_placeholders'][topic_name]
        if topic_name in ui_state['topic_inputs']:
            del ui_state['topic_inputs'][topic_name]
        # 更新显示
        update_display_func()


def on_subscribe_topic_click(ros_manager: ROSManager, topic_name: str):
    """订阅Topic按钮点击事件
    
    Args:
        ros_manager: ROS管理器实例
        topic_name: topic名称
    """
    ros_manager.subscribe_topic(topic_name)


def on_unsubscribe_topic_click(ros_manager: ROSManager, topic_name: str):
    """取消订阅Topic按钮点击事件
    
    Args:
        ros_manager: ROS管理器实例
        topic_name: topic名称
    """
    ros_manager.unsubscribe_topic(topic_name)


def on_update_topic_click(ros_manager: ROSManager, topic_name: str, topic_name_input, msg_type_input):
    """更新Topic配置按钮点击事件
    
    Args:
        ros_manager: ROS管理器实例
        topic_name: 原始topic名称
        topic_name_input: topic名称输入框
        msg_type_input: 消息类型输入框
    """
    new_topic_name = topic_name_input.value.strip()
    new_msg_type = msg_type_input.value.strip()
    
    if not new_topic_name:
        ui.notify("Topic名称不能为空", type='warning')
        return
    
    # 如果topic名称改变了，需要先移除旧的再添加新的
    if new_topic_name != topic_name:
        # 先取消订阅旧的
        ros_manager.unsubscribe_topic(topic_name)
        # 移除旧的
        ros_manager.remove_topic(topic_name)
        # 添加新的
        ros_manager.add_topic(new_topic_name, new_msg_type)
        # 更新UI显示
        if 'update_topics_display' in ui_state:
            ui_state['update_topics_display']()
    else:
        # 只更新消息类型 - 需要重新订阅
        ros_manager.unsubscribe_topic(topic_name)
        # 更新配置
        if topic_name in ros_manager.topic_configs:
            ros_manager.topic_configs[topic_name]['msg_type'] = new_msg_type
        ui.notify(f"✅ 更新Topic {topic_name} 配置成功", type='positive')


def update_topic_image(topic_name: str, img_base64: str):
    """更新指定topic的图像显示
    
    Args:
        topic_name: topic名称
        img_base64: base64编码的图像数据
    """
    if topic_name in ui_state['image_placeholders']:
        ui_state['image_placeholders'][topic_name].set_source(f"data:image/png;base64,{img_base64}")
    
    # 同时更新主图像显示（可选）
    if 'main_image' in ui_state:
        ui_state['main_image'].set_source(f"data:image/png;base64,{img_base64}")


def update_topic_message(topic_name: str, message: str):
    """更新指定topic的消息显示
    
    Args:
        topic_name: topic名称
        message: 消息内容
    """
    if topic_name in ui_state['message_placeholders']:
        ui_state['message_placeholders'][topic_name].set_text(message)
