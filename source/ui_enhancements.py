"""
UI模块 - 函数式编程实现
提供ROS服务和文字topic的UI组件
"""
from nicegui import ui
from typing import Dict, Callable, Optional
from ros_services import create_service_request_ui, COMMON_SERVICE_TYPES
from text_message_handler import create_text_topic_ui, TextTopicManager


# ==================== 状态管理函数 ====================

def create_ui_state() -> Dict:
    """创建UI状态字典"""
    return {
        'topics_container': None,
        'text_topics_container': None,
        'services_container': None
    }


# ==================== 面板创建函数 ====================

def create_image_topics_panel(ui_state: Dict, ros_manager):
    """创建图像topic面板"""
    ui.label("图像Topic管理").classes("text-lg font-bold mb-3")
    
    # 添加新topic
    with ui.row().classes("items-center gap-2 mb-3"):
        topic_input = ui.input("Topic名称", value="/image_raw").classes("w-40")
        type_input = ui.input("消息类型", value="sensor_msgs/Image").classes("w-40")
        ui.button("添加", 
                 on_click=lambda: on_add_image_topic(topic_input.value, type_input.value, ui_state, ros_manager))
    
    # topic列表容器
    topics_container = ui.column().classes("w-full")
    ui_state['topics_container'] = topics_container
    update_image_topics_display(ui_state, ros_manager)


def create_text_topics_panel(ui_state: Dict, text_topic_manager):
    """创建文字topic面板"""
    ui.label("文字Topic管理").classes("text-lg font-bold mb-3")
    
    # 添加新文字topic
    with ui.row().classes("items-center gap-2 mb-3"):
        topic_input = ui.input("Topic名称", value="/chatter").classes("w-40")
        type_input = ui.input("消息类型", value="std_msgs/String").classes("w-40")
        ui.button("添加", 
                 on_click=lambda: on_add_text_topic(topic_input.value, type_input.value, ui_state, text_topic_manager))
    
    # 文字topic列表容器
    text_topics_container = ui.column().classes("w-full")
    ui_state['text_topics_container'] = text_topics_container
    update_text_topics_display(ui_state, text_topic_manager)


def create_services_panel(ui_state: Dict, service_manager):
    """创建服务面板"""
    ui.label("ROS服务管理").classes("text-lg font-bold mb-3")
    
    # 检查service_manager是否可用
    if service_manager is None:
        ui.label("请先连接ROS以启用服务管理").classes("text-gray-500 mb-3")
        services_container = ui.column().classes("w-full")
        ui_state['services_container'] = services_container
        return
    
    # 添加新服务
    with ui.row().classes("items-center gap-2 mb-3"):
        service_input = ui.input("服务名称", value="/service").classes("w-40")
        
        # 服务类型选择
        type_select = ui.select(
            options=list(COMMON_SERVICE_TYPES.keys()),
            value="std_srvs/Trigger",
            label="服务类型"
        ).classes("w-40")
        
        ui.button("添加", 
                 on_click=lambda: on_add_service(service_input.value, type_select.value, ui_state, service_manager))
    
    # 服务列表容器
    services_container = ui.column().classes("w-full")
    ui_state['services_container'] = services_container
    update_services_display(ui_state, service_manager)


def create_status_panel(ros_manager, service_manager, text_topic_manager):
    """创建状态面板"""
    ui.label("系统状态").classes("text-lg font-bold mb-3")
    
    with ui.card().classes("w-full p-3"):
        # 连接状态
        with ui.row().classes("items-center gap-2"):
            status_dot = ui.icon("circle").classes("text-green-500" if ros_manager.is_connected else "text-red-500")
            status_text = "已连接" if ros_manager.is_connected else "未连接"
            ui.label(f"ROS连接: {status_text}")
        
        # Topic统计
        with ui.row().classes("items-center gap-3 mt-2"):
            image_count = len([t for t in ros_manager.get_topic_list() 
                              if ros_manager.topic_configs.get(t, {}).get('msg_type') == 'sensor_msgs/Image'])
            text_count = len(text_topic_manager.get_text_topic_list())
            service_count = 0 if service_manager is None else len(service_manager.get_service_list())
            
            ui.label(f"图像Topic: {image_count}")
            ui.label(f"文字Topic: {text_count}")
            ui.label(f"服务: {service_count}")


# ==================== 事件处理函数 ====================

def on_add_image_topic(topic_name: str, msg_type: str, ui_state: Dict, ros_manager):
    """添加图像topic"""
    if not topic_name.strip():
        ui.notify("Topic名称不能为空", type='warning')
        return
    
    if ros_manager.add_topic(topic_name, msg_type):
        update_image_topics_display(ui_state, ros_manager)
    else:
        ui.notify(f"Topic {topic_name} 已存在", type='warning')


def on_add_text_topic(topic_name: str, msg_type: str, ui_state: Dict, text_topic_manager):
    """添加文字topic"""
    if not topic_name.strip():
        ui.notify("Topic名称不能为空", type='warning')
        return
    
    if text_topic_manager.add_text_topic(topic_name, msg_type):
        update_text_topics_display(ui_state, text_topic_manager)
    else:
        ui.notify(f"文字Topic {topic_name} 添加失败", type='warning')


def on_add_service(service_name: str, service_type: str, ui_state: Dict, service_manager):
    """添加服务"""
    if not service_name.strip():
        ui.notify("服务名称不能为空", type='warning')
        return
    
    if service_manager.add_service(service_name, service_type):
        update_services_display(ui_state, service_manager)
    else:
        ui.notify(f"服务 {service_name} 添加失败", type='warning')


def on_call_service(service_name: str, request_data: Dict, service_manager):
    """调用服务"""
    result = service_manager.call_service(service_name, request_data)
    if result:
        ui.notify(f"服务 {service_name} 调用成功", type='positive')
    else:
        ui.notify(f"服务 {service_name} 调用失败", type='negative')


def on_remove_image_topic(topic_name: str, ui_state: Dict, ros_manager):
    """移除图像topic"""
    if ros_manager.remove_topic(topic_name):
        update_image_topics_display(ui_state, ros_manager)


def on_remove_text_topic(topic_name: str, ui_state: Dict, text_topic_manager):
    """移除文字topic"""
    if text_topic_manager.remove_text_topic(topic_name):
        update_text_topics_display(ui_state, text_topic_manager)


def on_remove_service(service_name: str, ui_state: Dict, service_manager):
    """移除服务"""
    if service_manager.remove_service(service_name):
        update_services_display(ui_state, service_manager)


# ==================== 更新显示函数 ====================

def update_image_topics_display(ui_state: Dict, ros_manager):
    """更新图像topic显示"""
    container = ui_state.get('topics_container')
    if not container:
        return
    
    container.clear()
    
    for topic_name in ros_manager.get_topic_list():
        config = ros_manager.topic_configs.get(topic_name, {})
        if config.get('msg_type') == 'sensor_msgs/Image':
            with container:
                create_image_topic_card(topic_name, config, ui_state, ros_manager)


def update_text_topics_display(ui_state: Dict, text_topic_manager):
    """更新文字topic显示"""
    container = ui_state.get('text_topics_container')
    if not container:
        return
    
    container.clear()
    
    for topic_name in text_topic_manager.get_text_topic_list():
        with container:
            history = text_topic_manager.get_message_history(topic_name)
            create_text_topic_ui(
                topic_name,
                history,
                on_subscribe=lambda tn: text_topic_manager.subscribe_text_topic(tn),
                on_unsubscribe=lambda tn: text_topic_manager.unsubscribe_text_topic(tn),
                on_remove=lambda tn: on_remove_text_topic(tn, ui_state, text_topic_manager)
            )


def update_services_display(ui_state: Dict, service_manager):
    """更新服务显示"""
    container = ui_state.get('services_container')
    if not container:
        return
    
    container.clear()
    
    # 检查service_manager是否可用
    if service_manager is None:
        return
    
    for service_name in service_manager.get_service_list():
        with container:
            create_service_card(service_name, service_manager, ui_state)


# ==================== 卡片创建函数 ====================

def create_image_topic_card(topic_name: str, config: Dict, ui_state: Dict, ros_manager):
    """创建图像topic卡片"""
    with ui.card().classes("w-full mb-2 p-2"):
        with ui.row().classes("items-center justify-between w-full"):
            ui.label(f"{topic_name}").classes("font-medium")
            
            status = "✅ 已订阅" if config.get('subscribed') else "⏸️ 未订阅"
            ui.label(status).classes("text-xs")
        
        with ui.row().classes("text-xs text-gray-600"):
            ui.label(f"类型: {config.get('msg_type', '未知')}")
            ui.label(f"消息数: {config.get('frame_count', 0)}")
        
        with ui.row().classes("gap-1 mt-1"):
            if not config.get('subscribed'):
                ui.button("订阅", 
                         on_click=lambda: ros_manager.subscribe_topic(topic_name),
                         color="green").classes("text-xs")
            else:
                ui.button("取消订阅", 
                         on_click=lambda: ros_manager.unsubscribe_topic(topic_name),
                         color="orange").classes("text-xs")
            
            ui.button("删除", 
                     on_click=lambda: on_remove_image_topic(topic_name, ui_state, ros_manager),
                     color="red").classes("text-xs")


def create_service_card(service_name: str, service_manager, ui_state: Dict):
    """创建服务卡片"""
    # 获取服务类型
    service_type = "未知"
    if service_name in service_manager.services:
        service_type = service_manager.services[service_name].service_type
    
    # 创建UI
    create_service_request_ui(
        service_name,
        service_type,
        on_call=lambda data: on_call_service(service_name, data, service_manager)
    )


# ==================== 主UI创建函数 ====================

def create_main_ui(ros_manager, service_manager, text_topic_manager):
    """创建主UI"""
    # 创建UI状态
    ui_state = create_ui_state()
    
    # 创建主布局
    with ui.header().classes("bg-blue-600 text-white p-3"):
        ui.label("ROS多功能管理器").classes("text-xl font-bold")
    
    with ui.row().classes("w-full h-screen p-3"):
        # 左侧配置面板
        with ui.column().classes("w-1/3 pr-3 h-full overflow-y-auto"):
            # 连接状态
            create_status_panel(ros_manager, service_manager, text_topic_manager)
            ui.separator().classes("my-3")
            
            # 图像topic管理
            create_image_topics_panel(ui_state, ros_manager)
            ui.separator().classes("my-3")
            
            # 文字topic管理
            create_text_topics_panel(ui_state, text_topic_manager)
            ui.separator().classes("my-3")
            
            # 服务管理
            create_services_panel(ui_state, service_manager)
        
        # 右侧显示面板
        with ui.column().classes("w-2/3 pl-3 h-full overflow-y-auto"):
            ui.label("实时显示").classes("text-lg font-bold mb-3")
            
            # 图像显示
            image_display = ui.image("").classes("w-full border rounded-lg")
            image_display.set_source("data:,")
            
            # 消息显示
            ui.label("消息日志").classes("text-md font-medium mt-3")
            messages_area = ui.column().classes("mt-2 p-2 bg-gray-50 rounded w-full h-48 overflow-y-auto")
    
    return ui_state
