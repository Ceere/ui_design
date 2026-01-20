from nicegui import ui
from ui_function.topic_controller import handle_topic_click
from ui_function.get_object import get_object_instance
from ros.ros_topic import RosTopic
from ui_function.image_process import handle_image_message
from ui_function.bridge_controller import BridgeController

import logging
import asyncio

device_instance,ros_bridge_instance,ssh_instance = get_object_instance()
bridge_controller = BridgeController()

@ui.page('/topic_page')
def topic_page():
    ui.page_title('Qualcomm Robotics SDK Tools')
    
    # 标题栏区域
    with ui.header(elevated=True).style('background-color: #4f6db9'):
        ui.link('Qualcomm Robotics SDK', '/').classes('text-red-500')
        ui.link('Topic', '/topic_page').classes('text-red-500')
    
    # 主内容区域 - 数据展示
    with ui.column().classes('w-full p-4'):

        ui.label('Topic').classes('text-h5 font-bold mt-4')

        # 内容显示
        with ui.card().classes('w-full mt-4'):
            # 消息显示区域
            topic_name_type = ui.label('Please select topic to view').classes('text-body1 mt-2')
            
            # 消息内容区域（使用代码块显示格式化的消息）
            message_content = ui.label().classes('w-full mt-2 max-h-96 overflow-auto')
            # 使用原生HTML img标签避免闪烁，配合JavaScript直接更新
            ui.html('<img id="video_frame" style="width:100%; height:auto; background: #000; border-radius: 8px; object-fit: contain; display: none;" />', sanitize=False)
            
            def update_message_display():
                """更新消息显示"""
                if RosTopic.cls_latest_message:
                    topic_name_type.set_text(f'Subscribe Topic {RosTopic.cls_current_topic_name}, Topic type is {RosTopic.cls_current_topic_type}')

                    if RosTopic.cls_current_topic_type == 'sensor_msgs/msg/Image':
                        # 显示图片，隐藏文本
                        image_origin = RosTopic.cls_latest_message
                        img_base64 = handle_image_message(image_origin)
                        if img_base64:
                            # 使用JavaScript直接更新img标签，避免闪烁
                            ui.run_javascript(f'''
                                const img = document.getElementById("video_frame");
                                if (img) {{
                                    img.src = "data:image/png;base64,{img_base64}";
                                    img.style.display = "block";
                                }}
                            ''')
                            message_content.set_visibility(False)
                        else:
                            # 如果图片处理失败，显示错误信息
                            message_content.set_text("不支持处理该类型图片格式")
                            message_content.set_visibility(True)
                            ui.run_javascript('''
                                const img = document.getElementById("video_frame");
                                if (img) {
                                    img.style.display = "none";
                                }
                            ''')
                    elif RosTopic.cls_current_topic_type == 'std_msgs/msg/String':
                        # 显示文本，隐藏图片
                        message_content.set_text(RosTopic.cls_latest_message['data'])
                        message_content.set_visibility(True)
                        ui.run_javascript('''
                            const img = document.getElementById("video_frame");
                            if (img) {
                                img.style.display = "none";
                            }
                        ''')
                    else:
                        # 其他类型的消息
                        message_content.set_text(f"消息类型: {RosTopic.cls_current_topic_type}\n数据: {str(RosTopic.cls_latest_message)}")
                        message_content.set_visibility(True)
                        ui.run_javascript('''
                            const img = document.getElementById("video_frame");
                            if (img) {
                                img.style.display = "none";
                            }
                        ''')
                else:
                    # 没有消息时，显示提示信息
                    topic_name_type.set_text('Please select topic to view')
                    message_content.set_text('')
                    message_content.set_visibility(True)
                    ui.run_javascript('''
                        const img = document.getElementById("video_frame");
                        if (img) {
                            img.style.display = "none";
                        }
                    ''')
            
            # 添加定时器更新消息显示
            ui.timer(0.1, update_message_display)

    # 左边栏区域
    with ui.left_drawer().style('background-color: #d7e3f4'):
        # 状态栏区域
        with ui.card().style('background-color: #ffffff; margin-bottom: 5px;'):
            with ui.card_section():
                ui.label('Device Status').classes('text-h6 font-bold')

                # 状态信息
                ip_text = ui.label('IP: Disconnected').classes('text-body2')
                ros_host_label = ui.label('Ros Bridge Port: Disconnected').classes('text-body2')
                ssh_status_label = ui.label('SSH: Disconnected').classes('text-body2')
                update_time_label = ui.label('N/A').classes('text-body2 text-grey')

                def update_status_display():
                    """更新状态栏显示"""
                    # 更新UI标签
                    if ros_bridge_instance.ros_is_connected:
                        ip_text.set_text(f"IP: {ros_bridge_instance.ros_host}")
                        ros_host_label.set_text(f"Ros Bridge Port: {ros_bridge_instance.ros_port}")

                    # 显示SSH状态
                    if ssh_instance.is_connected is True:
                        ssh_host_port = f"{ssh_instance.hostname}:{ssh_instance.port}"
                        ssh_status_label.set_text(f"SSH: {ssh_host_port}")

                    # 更新时间
                    import datetime
                    update_time_label.set_text(datetime.datetime.now().strftime('%H:%M:%S'))
        # Topic process
        with ui.column():
            ui.label('ROS Topics').classes('text-h6 font-bold mt-6')
            
            # Topic列表容器
            topic_list_item = ui.dropdown_button("Select Topic", auto_close=True)
            
            async def refresh_topics():
                """异步刷新topic列表"""
                # 清空下拉菜单
                topic_list_item.clear()
                
                # 显示加载状态
                topic_list_item.props('loading')
                
                try:
                    # 在后台线程中执行耗时操作，避免阻塞UI
                    loop = asyncio.get_event_loop()
                    topic_list = await loop.run_in_executor(
                        None,  # 使用默认线程池
                        bridge_controller.get_all_topics
                    )
                    
                    logging.info(f"刷新topic列表，获取到 {len(topic_list)} 个topics")
                    
                    # 添加topic项到下拉菜单
                    with topic_list_item:
                        for topic in topic_list:
                            topic_name = topic['name']
                            ui.item(topic_name, on_click=lambda t=topic: handle_topic_click(t))
                            
                except Exception as e:
                    logging.error(f"刷新topic列表失败: {e}")
                    ui.notify(f"获取topic列表失败: {e}", type='negative', position='top')
                finally:
                    # 移除加载状态
                    topic_list_item.props(remove='loading')
            
            def on_topic_button_click():
                """处理topic按钮点击事件"""
                asyncio.create_task(refresh_topics())
            
            # 设置点击事件，点击下拉按钮时刷新topic列表
            topic_list_item.on_click(on_topic_button_click)

    def update_timer():
        # 定时更新状态栏
        ui.timer(1.0, update_status_display)
    
    update_timer()
