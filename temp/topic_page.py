"""
Topic页面 - 显示当前订阅的topic的数据展示
分为左右两侧：左侧topic选择订阅，右侧数据展示
"""
from nicegui import ui
from typing import Dict, Callable, List
from temp.ros_connection_manager import ROSManager

@ui.page('/topic_page')
def topic_page():
    ui.page_title('Qualcomm Robotics SDK Tools')
    with ui.header(elevated=True).style('background-color: #4f6db9'):
        ui.link('Qualcomm Robotics SDK', '/').classes('text-red-500')
        ui.link('Connect device', '/connect_device').classes('text-red-500')
        ui.link('Topic', '/topic_page').classes('text-red-500')
    

def create_topic_page(ros_manager: ROSManager, on_navigate_back: Callable) -> Dict:
    """创建Topic页面
    
    Args:
        ros_manager: ROS管理器实例
        on_navigate_back: 返回连接页面的回调函数
        
    Returns:
        Dict: 页面状态字典
    """
    # 页面状态
    page_state = {
        'selected_topic': None,
        'topic_select': None,
        'refresh_button': None,
        'subscribe_button': None,
        'unsubscribe_button': None,
        'image_display': None,
        'text_display': None,
        'topic_info_container': None,
        'available_topics_container': None
    }
    
    # 页面标题和返回按钮
    with ui.row().classes("w-full items-center mb-6"):
        ui.button("← 返回连接页面", 
                 on_click=on_navigate_back,
                 color="gray").classes("mr-4")
        ui.label("Topic数据展示").classes("text-2xl font-bold text-blue-600")
    
    # 两列布局
    with ui.row().classes("w-full h-[calc(100vh-150px)] gap-6"):
        # 左侧：Topic选择和管理 (1/3宽度)
        with ui.column().classes("w-1/3 h-full overflow-y-auto border-r-2 pr-4"):
            create_topic_selection_section(page_state, ros_manager)
        
        # 右侧：数据展示 (2/3宽度)
        with ui.column().classes("w-2/3 h-full overflow-y-auto"):
            create_data_display_section(page_state, ros_manager)
    
    # 初始更新
    update_topic_selection(page_state, ros_manager)
    
    return page_state


def create_topic_selection_section(page_state: Dict, ros_manager: ROSManager):
    """创建Topic选择部分
    
    Args:
        page_state: 页面状态字典
        ros_manager: ROS管理器实例
    """
    with ui.card().classes("w-full mb-4"):
        ui.label("Topic选择与订阅").classes("text-xl font-bold mb-4")
        
        # 已配置的Topic选择
        with ui.row().classes("items-center gap-2 mb-3"):
            page_state['topic_select'] = ui.select(
                options=[],
                label="选择已配置的Topic",
                with_input=True
            ).classes("w-64")
            
            page_state['refresh_button'] = ui.button("刷新", 
                                                    on_click=lambda: update_topic_selection(page_state, ros_manager))
        
        # 订阅/取消订阅按钮
        with ui.row().classes("gap-2 mb-4"):
            page_state['subscribe_button'] = ui.button("订阅选中Topic", 
                                                      on_click=lambda: on_subscribe_selected_topic(page_state, ros_manager),
                                                      color="green")
            
            page_state['unsubscribe_button'] = ui.button("取消订阅选中Topic", 
                                                        on_click=lambda: on_unsubscribe_selected_topic(page_state, ros_manager),
                                                        color="orange")
        
        # Topic信息显示
        page_state['topic_info_container'] = ui.column().classes("w-full")
        
        # 设置选择回调
        page_state['topic_select'].on_value_change(lambda e: on_topic_selected(e.value, page_state, ros_manager))
    
    # 可用的Topic列表
    with ui.card().classes("w-full"):
        ui.label("ROS系统中可用的Topics").classes("text-xl font-bold mb-4")
        
        page_state['available_topics_container'] = ui.column().classes("w-full")
        
        ui.button("刷新可用Topic列表", 
                 on_click=lambda: update_available_topics(page_state, ros_manager),
                 color="blue").classes("w-full mt-2")


def create_data_display_section(page_state: Dict, ros_manager: ROSManager):
    """创建数据展示部分
    
    Args:
        page_state: 页面状态字典
        ros_manager: ROS管理器实例
    """
    with ui.card().classes("w-full h-full"):
        ui.label("实时数据展示").classes("text-xl font-bold mb-4")
        
        # 标签页：图像和文本
        with ui.tabs().classes("w-full") as tabs:
            image_tab = ui.tab('图像数据')
            text_tab = ui.tab('文本数据')
            info_tab = ui.tab('Topic信息')
        
        with ui.tab_panels(tabs, value=image_tab).classes("w-full h-full"):
            # 图像显示面板
            with ui.tab_panel(image_tab):
                ui.label("图像显示").classes("text-lg font-semibold mb-2")
                page_state['image_display'] = ui.image("").classes("w-full h-[400px] border rounded-lg object-contain")
                page_state['image_display'].set_source("data:,")
                
                # 图像信息
                with ui.row().classes("mt-2 text-sm text-gray-600"):
                    ui.label("状态: 等待图像数据...")
            
            # 文本显示面板
            with ui.tab_panel(text_tab):
                ui.label("文本数据").classes("text-lg font-semibold mb-2")
                page_state['text_display'] = ui.textarea("").classes("w-full h-[400px] font-mono text-sm border rounded")
                page_state['text_display'].props("readonly")
                page_state['text_display'].value = "等待文本数据..."
                
                # 文本信息
                with ui.row().classes("mt-2 text-sm text-gray-600"):
                    ui.label("消息格式: JSON/文本")
            
            # Topic信息面板
            with ui.tab_panel(info_tab):
                ui.label("Topic详细信息").classes("text-lg font-semibold mb-2")
                
                info_container = ui.column().classes("w-full p-4 border rounded")
                with info_container:
                    ui.label("请选择一个Topic以查看详细信息").classes("text-gray-500 italic")


def update_topic_selection(page_state: Dict, ros_manager: ROSManager):
    """更新Topic选择列表
    
    Args:
        page_state: 页面状态字典
        ros_manager: ROS管理器实例
    """
    topic_select = page_state.get('topic_select')
    if not topic_select:
        return
    
    # 获取已配置的Topic列表
    topic_list = ros_manager.get_topic_list()
    
    if topic_list:
        options = []
        for topic_name in topic_list:
            config = ros_manager.topic_configs.get(topic_name, {})
            status = "✅" if config.get('subscribed') else "⏸️"
            options.append(f"{status} {topic_name}")
        
        topic_select.options = options
        
        # 如果没有选中的Topic，选择第一个
        if not page_state['selected_topic'] and options:
            topic_select.value = options[0]
            on_topic_selected(options[0], page_state, ros_manager)
    else:
        topic_select.options = []
        topic_select.value = None
        page_state['selected_topic'] = None
    
    # 更新按钮状态
    update_button_states(page_state, ros_manager)


def update_available_topics(page_state: Dict, ros_manager: ROSManager):
    """更新可用的Topic列表
    
    Args:
        page_state: 页面状态字典
        ros_manager: ROS管理器实例
    """
    container = page_state.get('available_topics_container')
    if not container:
        return
    
    container.clear()
    
    if not ros_manager.is_connected:
        with container:
            ui.label("请先连接ROS以获取可用Topic列表").classes("text-gray-500 italic")
        return
    
    try:
        available_topics = ros_manager.get_available_topics()
        
        if not available_topics:
            with container:
                ui.label("未找到可用的Topic").classes("text-gray-500 italic")
            return
        
        for topic_info in available_topics:
            with container:
                create_available_topic_card(topic_info, ros_manager, page_state)
                
    except Exception as e:
        with container:
            ui.label(f"获取Topic列表失败: {str(e)}").classes("text-red-500")


def create_available_topic_card(topic_info: Dict, ros_manager: ROSManager, page_state: Dict):
    """创建可用Topic卡片
    
    Args:
        topic_info: Topic信息字典
        ros_manager: ROS管理器实例
        page_state: 页面状态字典
    """
    topic_name = topic_info.get('name', '')
    topic_type = topic_info.get('type', 'unknown')
    
    with ui.card().classes("w-full mb-2 p-2"):
        with ui.row().classes("items-center justify-between"):
            # Topic信息
            with ui.column().classes("gap-1"):
                ui.label(topic_name).classes("font-medium text-sm")
                ui.label(f"类型: {topic_type}").classes("text-xs text-gray-600")
            
            # 快速添加按钮
            is_configured = topic_name in ros_manager.topic_configs
            if not is_configured:
                ui.button("快速添加", 
                         on_click=lambda tn=topic_name, tt=topic_type: on_quick_add_topic(tn, tt, ros_manager, page_state),
                         color="blue").classes("text-xs px-2")
            else:
                ui.label("已配置").classes("text-xs text-green-600")


def update_topic_info(page_state: Dict, ros_manager: ROSManager):
    """更新Topic信息显示
    
    Args:
        page_state: 页面状态字典
        ros_manager: ROS管理器实例
    """
    container = page_state.get('topic_info_container')
    if not container:
        return
    
    container.clear()
    
    topic_name = page_state.get('selected_topic')
    if not topic_name:
        with container:
            ui.label("请选择一个Topic").classes("text-gray-500 italic")
        return
    
    config = ros_manager.topic_configs.get(topic_name, {})
    
    with container:
        # Topic基本信息
        with ui.card().classes("w-full p-3"):
            ui.label("Topic信息").classes("font-bold mb-2")
            
            with ui.column().classes("gap-1 text-sm"):
                ui.label(f"名称: {topic_name}")
                ui.label(f"消息类型: {config.get('msg_type', '未知')}")
                ui.label(f"订阅状态: {'✅ 已订阅' if config.get('subscribed') else '⏸️ 未订阅'}")
                ui.label(f"接收消息数: {config.get('frame_count', 0)}")
                ui.label(f"最新消息时间: {config.get('last_update', '暂无')}")
        
        # 最新消息预览
        latest_message = ros_manager.get_latest_message(topic_name)
        if latest_message:
            with ui.card().classes("w-full p-3 mt-2"):
                ui.label("最新消息预览").classes("font-bold mb-2")
                
                # 尝试格式化显示消息
                try:
                    if hasattr(latest_message, '__dict__'):
                        # 如果是ROS消息对象
                        message_str = str(latest_message.__dict__)
                    else:
                        message_str = str(latest_message)
                    
                    # 截断过长的消息
                    if len(message_str) > 200:
                        message_str = message_str[:200] + "..."
                    
                    ui.textarea(value=message_str).classes("w-full h-24 text-xs").props("readonly")
                except:
                    ui.label("无法显示消息内容").classes("text-gray-500")


def update_button_states(page_state: Dict, ros_manager: ROSManager):
    """更新按钮状态
    
    Args:
        page_state: 页面状态字典
        ros_manager: ROS管理器实例
    """
    topic_name = page_state.get('selected_topic')
    
    # 更新订阅/取消订阅按钮状态
    if topic_name and topic_name in ros_manager.topic_configs:
        config = ros_manager.topic_configs[topic_name]
        is_subscribed = config.get('subscribed', False)
        
        if page_state.get('subscribe_button'):
            page_state['subscribe_button'].props(f"disabled={is_subscribed}")
        
        if page_state.get('unsubscribe_button'):
            page_state['unsubscribe_button'].props(f"disabled={not is_subscribed}")
    else:
        # 没有选中的Topic，禁用所有按钮
        if page_state.get('subscribe_button'):
            page_state['subscribe_button'].props("disabled")
        
        if page_state.get('unsubscribe_button'):
            page_state['unsubscribe_button'].props("disabled")


# ==================== 事件处理函数 ====================

def on_topic_selected(topic_option: str, page_state: Dict, ros_manager: ROSManager):
    """Topic选择回调
    
    Args:
        topic_option: 选择的Topic选项字符串
        page_state: 页面状态字典
        ros_manager: ROS管理器实例
    """
    if not topic_option:
        return
    
    # 解析Topic名称（移除状态图标）
    if " " in topic_option:
        topic_name = topic_option.split(" ", 1)[1]
    else:
        topic_name = topic_option
    
    page_state['selected_topic'] = topic_name
    
    # 更新Topic信息显示
    update_topic_info(page_state, ros_manager)
    
    # 更新按钮状态
    update_button_states(page_state, ros_manager)
    
    # 注册UI回调
    def image_callback(img_base64):
        if page_state.get('image_display'):
            page_state['image_display'].set_source(f"data:image/png;base64,{img_base64}")
    
    def text_callback(msg):
        if page_state.get('text_display'):
            try:
                # 尝试格式化消息
                if hasattr(msg, '__dict__'):
                    import json
                    try:
                        formatted_msg = json.dumps(msg.__dict__, indent=2, default=str)
                    except:
                        formatted_msg = str(msg.__dict__)
                else:
                    formatted_msg = str(msg)
                
                page_state['text_display'].value = formatted_msg
            except Exception as e:
                page_state['text_display'].value = f"无法格式化消息: {str(e)}\n原始消息: {str(msg)}"
    
    ros_manager.register_ui_callbacks(
        topic_name,
        image_callback=image_callback,
        message_callback=text_callback
    )
    
    # 如果有最新消息，立即显示
    latest_message = ros_manager.get_latest_message(topic_name)
    if latest_message and page_state.get('text_display'):
        text_callback(latest_message)


def on_subscribe_selected_topic(page_state: Dict, ros_manager: ROSManager):
    """订阅选中Topic
    
    Args:
        page_state: 页面状态字典
        ros_manager: ROS管理器实例
    """
    topic_name = page_state.get('selected_topic')
    if not topic_name:
        ui.notify("请先选择一个Topic", type='warning')
        return
    
    if ros_manager.subscribe_topic(topic_name):
        # 更新显示
        update_topic_selection(page_state, ros_manager)
        update_topic_info(page_state, ros_manager)


def on_unsubscribe_selected_topic(page_state: Dict, ros_manager: ROSManager):
    """取消订阅选中Topic
    
    Args:
        page_state: 页面状态字典
        ros_manager: ROS管理器实例
    """
    topic_name = page_state.get('selected_topic')
    if not topic_name:
        ui.notify("请先选择一个Topic", type='warning')
        return
    
    if ros_manager.unsubscribe_topic(topic_name):
        # 更新显示
        update_topic_selection(page_state, ros_manager)
        update_topic_info(page_state, ros_manager)


def on_quick_add_topic(topic_name: str, topic_type: str, ros_manager: ROSManager, page_state: Dict):
    """快速添加Topic
    
    Args:
        topic_name: Topic名称
        topic_type: Topic类型
        ros_manager: ROS管理器实例
        page_state: 页面状态字典
    """
    if ros_manager.add_topic(topic_name, topic_type):
        ui.notify(f"✅ 已添加Topic: {topic_name}", type='positive')
        
        # 更新Topic选择列表
        update_topic_selection(page_state, ros_manager)
        
        # 自动选择新添加的Topic
        topic_select = page_state.get('topic_select')
        if topic_select:
            for option in topic_select.options:
                if topic_name in option:
                    topic_select.value = option
                    on_topic_selected(option, page_state, ros_manager)
                    break
    else:
        ui.notify(f"⚠️ Topic {topic_name} 已存在", type='warning')
