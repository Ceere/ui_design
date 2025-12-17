"""
简单UI模块 - 函数式编程实现
提供简洁的ROS topic选择和数据显示界面
"""
import logging
from nicegui import ui
from typing import Dict, Callable, Optional, List
from text_message_handler import TextMessageProcessor


def create_ui_state() -> Dict:
    """创建UI状态字典
    
    Returns:
        Dict: UI状态字典
    """
    return {
        'selected_topic': None,
        'topic_select': None,
        'refresh_button': None,
        'subscribe_button': None,
        'unsubscribe_button': None,
        'image_display': None,
        'message_display': None,
        'status_label': None,
        'message_processor': TextMessageProcessor()
    }


def create_connection_panel(ui_state: Dict, ros_manager, on_connect: Callable, on_disconnect: Callable):
    """创建连接面板
    
    Args:
        ui_state: UI状态字典
        ros_manager: ROS管理器
        on_connect: 连接回调函数
        on_disconnect: 断开连接回调函数
    """
    with ui.card().classes("w-full mb-4"):  # 卡片：全宽，下边距4
        ui.label("ROS连接").classes("text-lg font-bold mb-2")  # 标签：大号文字，粗体，下边距2
        
        with ui.row().classes("items-center gap-2"):  # 行：垂直居中，元素间距2
            host_input = ui.input("主机", value="localhost").classes("w-40")  # 输入框：宽度40
            port_input = ui.number("端口", value=9090, min=1, max=65535).classes("w-32")  # 数字输入：宽度32
            
            ui.button("连接", 
                     on_click=lambda: on_connect(host_input.value, int(port_input.value)))
            ui.button("断开", 
                     on_click=on_disconnect,
                     color="red")
            
            # 连接状态指示器
            status_dot = ui.icon("circle").classes("text-red-500")  # 图标：红色
            ui_state['status_dot'] = status_dot


def create_topic_selection_panel(ui_state: Dict, ros_manager, on_topic_selected: Callable):
    """创建topic选择面板
    
    Args:
        ui_state: UI状态字典
        ros_manager: ROS管理器
        on_topic_selected: topic选择回调函数
    """
    with ui.card().classes("w-full mb-4"):  # 卡片：全宽，下边距4
        ui.label("Topic选择").classes("text-lg font-bold mb-2")  # 标签：大号文字，粗体，下边距2
        
        with ui.row().classes("items-center gap-2"):  # 行：垂直居中，元素间距2
            # Topic下拉选择框
            topic_select = ui.select(
                options=[],
                label="选择Topic",
                with_input=True
            ).classes("w-64")  # 选择框：宽度64
            ui_state['topic_select'] = topic_select
            
            # 刷新按钮
            refresh_button = ui.button("刷新", 
                                      on_click=lambda: refresh_topic_list(ui_state, ros_manager))
            ui_state['refresh_button'] = refresh_button
            
            # 订阅/取消订阅按钮
            subscribe_button = ui.button("订阅", 
                                        on_click=lambda: on_subscribe_click(ui_state, ros_manager),
                                        color="green")
            ui_state['subscribe_button'] = subscribe_button
            
            unsubscribe_button = ui.button("取消订阅", 
                                          on_click=lambda: on_unsubscribe_click(ui_state, ros_manager),
                                          color="orange")
            ui_state['unsubscribe_button'] = unsubscribe_button
        
        # Topic信息显示
        with ui.row().classes("mt-2 text-sm"):  # 行：上边距2，小号文字
            topic_type_label = ui.label("类型: 未选择").classes("text-gray-600")  # 标签：灰色文字
            ui_state['topic_type_label'] = topic_type_label
            
            message_count_label = ui.label("消息数: 0").classes("text-gray-600 ml-4")  # 标签：灰色文字，左外边距4
            ui_state['message_count_label'] = message_count_label
        
        # 设置选择回调
        topic_select.on_value_change(lambda e: on_topic_selected(e.value, ui_state, ros_manager))


def create_display_panel(ui_state: Dict):
    """创建数据显示面板 - 统一的消息展示区
    
    Args:
        ui_state: UI状态字典
    """
    with ui.card().classes("w-full h-full"):  # 卡片：全宽，全高
        ui.label("消息展示区").classes("text-lg font-bold mb-2")  # 标签：大号文字，粗体，下边距2
        
        # 标签页：图像和消息
        with ui.tabs().classes("w-full") as tabs:
            image_tab = ui.tab('图像')
            message_tab = ui.tab('消息内容')
        
        with ui.tab_panels(tabs, value=image_tab).classes("w-full h-full"):
            # 图像显示面板
            with ui.tab_panel(image_tab):
                image_display = ui.image("").classes("w-full h-96 border rounded-lg object-contain")  # 图像：全宽，高度96，边框，圆角，对象包含
                image_display.set_source("data:,")
                ui_state['image_display'] = image_display
            
            # 消息显示面板
            with ui.tab_panel(message_tab):
                message_display = ui.textarea("").classes("w-full h-96 font-mono text-sm border rounded")  # 文本域：全宽，高度96，等宽字体，小号文字，边框，圆角
                message_display.props("readonly")
                ui_state['message_display'] = message_display


def create_status_panel(ui_state: Dict, ros_manager):
    """创建状态面板
    
    Args:
        ui_state: UI状态字典
        ros_manager: ROS管理器
    """
    with ui.card().classes("w-full mb-4"):  # 卡片：全宽，下边距4
        ui.label("系统状态").classes("text-lg font-bold mb-2")  # 标签：大号文字，粗体，下边距2
        
        with ui.row().classes("items-center gap-4"):  # 行：垂直居中，元素间距4
            # 连接状态
            status_text = "已连接" if ros_manager.is_connected else "未连接"
            ui.label(f"ROS连接: {status_text}")
            
            # Topic数量
            topic_count = len(ros_manager.get_topic_list())
            ui.label(f"已配置Topic: {topic_count}")
            
            # 订阅数量
            subscribed_count = sum(1 for t in ros_manager.topic_configs.values() if t.get('subscribed'))
            ui.label(f"已订阅: {subscribed_count}")


def refresh_topic_list(ui_state: Dict, ros_manager):
    """刷新topic列表
    
    Args:
        ui_state: UI状态字典
        ros_manager: ROS管理器
    """
    if not ros_manager.is_connected:
        ui.notify("❌ 请先连接ROS", type='warning')
        return
    
    try:
        # 获取可用topic
        available_topics = ros_manager.get_available_topics()
        
        # 更新下拉选择框
        if ui_state['topic_select']:
            if available_topics:
                options = [f"{topic['name']} ({topic['type']})" for topic in available_topics]
                ui_state['topic_select'].options = options
                ui.notify(f"✅ 找到 {len(options)} 个topic", type='info')
            else:
                ui_state['topic_select'].options = []
                ui.notify("⚠️ 未找到可用topic，请检查ROS系统是否有发布的topic", type='warning')
    except Exception as e:
        logging.error(f"刷新topic列表失败: {e}")
        ui.notify(f"❌ 刷新topic列表失败: {str(e)}", type='negative')


def on_topic_selected(topic_info: str, ui_state: Dict, ros_manager):
    """topic选择回调
    
    Args:
        topic_info: topic信息字符串 (格式: "topic_name (topic_type)")
        ui_state: UI状态字典
        ros_manager: ROS管理器
    """
    if not topic_info:
        return
    
    # 解析topic名称和类型
    try:
        if " (" in topic_info and ")" in topic_info:
            topic_name = topic_info.split(" (")[0]
            topic_type = topic_info.split(" (")[1].rstrip(")")
        else:
            topic_name = topic_info
            topic_type = ros_manager.get_topic_type(topic_name)
        
        ui_state['selected_topic'] = topic_name
        
        # 更新UI显示
        if ui_state['topic_type_label']:
            ui_state['topic_type_label'].set_text(f"类型: {topic_type or '未知'}")
        
        # 更新消息计数
        if topic_name in ros_manager.topic_configs:
            count = ros_manager.topic_configs[topic_name].get('frame_count', 0)
            if ui_state['message_count_label']:
                ui_state['message_count_label'].set_text(f"消息数: {count}")
        
        # 注册回调
        def image_callback(img_base64):
            if ui_state['image_display']:
                ui_state['image_display'].set_source(f"data:image/png;base64,{img_base64}")
        
        def message_callback(msg):
            if ui_state['message_display']:
                # 处理消息
                processed = ui_state['message_processor'].process_message(topic_name, msg)
                formatted = ui_state['message_processor'].format_message_for_display(processed)
                ui_state['message_display'].value = formatted
        
        ros_manager.register_ui_callbacks(
            topic_name,
            image_callback=image_callback,
            message_callback=message_callback
        )
        
    except Exception as e:
        ui.notify(f"选择topic失败: {e}", type='negative')


def on_subscribe_click(ui_state: Dict, ros_manager):
    """订阅按钮点击回调
    
    Args:
        ui_state: UI状态字典
        ros_manager: ROS管理器
    """
    topic_name = ui_state.get('selected_topic')
    if not topic_name:
        ui.notify("请先选择topic", type='warning')
        return
    
    # 如果topic未配置，先添加配置
    if topic_name not in ros_manager.topic_configs:
        topic_type = ros_manager.get_topic_type(topic_name)
        if not topic_type:
            ui.notify("无法获取topic类型", type='negative')
            return
        
        ros_manager.add_topic(topic_name, topic_type)
    
    # 订阅topic
    if ros_manager.subscribe_topic(topic_name):
        ui.notify(f"已订阅 {topic_name}", type='positive')


def on_unsubscribe_click(ui_state: Dict, ros_manager):
    """取消订阅按钮点击回调
    
    Args:
        ui_state: UI状态字典
        ros_manager: ROS管理器
    """
    topic_name = ui_state.get('selected_topic')
    if not topic_name:
        ui.notify("请先选择topic", type='warning')
        return
    
    if ros_manager.unsubscribe_topic(topic_name):
        ui.notify(f"已取消订阅 {topic_name}", type='info')


def update_ui_status(ui_state: Dict, ros_manager):
    """更新UI状态
    
    Args:
        ui_state: UI状态字典
        ros_manager: ROS管理器
    """
    # 更新连接状态指示器
    if ui_state.get('status_dot'):
        color = "text-green-500" if ros_manager.is_connected else "text-red-500"  # 绿色表示已连接，红色表示未连接
        ui_state['status_dot'].classes(f"circle {color}")
    
    # 更新按钮状态
    if ui_state.get('refresh_button'):
        ui_state['refresh_button'].props(f"disabled={not ros_manager.is_connected}")  # 未连接时禁用刷新按钮
    
    if ui_state.get('subscribe_button'):
        topic_name = ui_state.get('selected_topic')
        is_subscribed = False
        if topic_name and topic_name in ros_manager.topic_configs:
            is_subscribed = ros_manager.topic_configs[topic_name].get('subscribed', False)
        
        ui_state['subscribe_button'].props(f"disabled={not topic_name or is_subscribed}")  # 未选择topic或已订阅时禁用订阅按钮
        ui_state['unsubscribe_button'].props(f"disabled={not topic_name or not is_subscribed}")  # 未选择topic或未订阅时禁用取消订阅按钮


def create_simple_ui(ros_manager, on_connect_callback: Callable, on_disconnect_callback: Callable):
    """创建简单UI
    
    Args:
        ros_manager: ROS管理器
        on_connect_callback: 连接回调函数
        on_disconnect_callback: 断开连接回调函数
        
    Returns:
        Dict: UI状态字典
    """
    # 创建UI状态
    ui_state = create_ui_state()
    
    # 创建主布局
    with ui.header().classes("bg-blue-400 text-white p-3"):  # 头部：蓝色背景，白色文字，内边距3
        ui.label("ROS Topic查看器").classes("text-xl font-bold")  # 标签：特大号文字，粗体
    
    with ui.row().classes("w-full h-screen p-3"):  # 行：全宽，全屏高度，内边距3
        # 左侧控制面板
        with ui.column().classes("w-1/3 pr-3 h-full overflow-y-auto"):  # 列：宽度1/3，右内边距3，全高，垂直滚动
            # 连接面板
            create_connection_panel(ui_state, ros_manager, on_connect_callback, on_disconnect_callback)
            
            # 状态面板
            create_status_panel(ui_state, ros_manager)
            
            # Topic选择面板
            create_topic_selection_panel(ui_state, ros_manager, on_topic_selected)
        
        # 右侧显示面板
        with ui.column().classes("w-2/3 pl-3 h-full"):  # 列：宽度2/3，左内边距3，全高
            create_display_panel(ui_state)
    
    # 初始更新UI状态
    update_ui_status(ui_state, ros_manager)
    
    return ui_state
