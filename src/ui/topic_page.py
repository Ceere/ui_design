from nicegui import ui
from ui_function.connect_device_controller import ConnectDeviceController
from ui_function.bridge_controller import BridgeController
from ui_function.topic_controller import handle_topic_click
from ros.ros_topic import RosTopic
from ui.image_process import handle_image_message
import logging

@ui.page('/topic_page')
def topic_page():
    ui.page_title('Qualcomm Robotics SDK Tools')
    
    # 创建控制器实例
    device_controller = ConnectDeviceController()
    bridge_controller = BridgeController()
    
    with ui.header(elevated=True).style('background-color: #4f6db9'):
        ui.link('Qualcomm Robotics SDK', '/').classes('text-red-500')
        ui.link('Topic', '/topic_page').classes('text-red-500')
    
    # 主内容区域 - 数据展示
    with ui.column().classes('w-full p-4'):
        # 数据展示标题
        ui.label('Topic').classes('text-h5 font-bold mt-4')
        
        # 消息显示区域
        with ui.card().classes('w-full mt-4'):
            # 消息显示区域
            topic_name_type = ui.label('Please select topic to view').classes('text-body1 mt-2')
            
            # 消息内容区域（使用代码块显示格式化的消息）
            message_content = ui.label().classes('w-full mt-2 max-h-96 overflow-auto')
            image_content = ui.image()
            
            def update_message_display():
                """更新消息显示"""
                if RosTopic.cls_latest_message:
                    topic_name_type.set_text(f'Subscribe Topic {RosTopic.cls_current_topic_name}, Topic type is {RosTopic.cls_current_topic_type}')

                    if RosTopic.cls_current_topic_type == 'sensor_msgs/msg/Image':
                        # 显示图片，隐藏文本
                        image_origin = RosTopic.cls_latest_message
                        img_base64 = handle_image_message(image_origin)
                        if img_base64:
                            image_content.set_source(f"data:image/png;base64,{img_base64}")
                            image_content.set_visibility(True)
                            message_content.set_visibility(False)
                        else:
                            # 如果图片处理失败，显示错误信息
                            message_content.set_text("无法处理图片消息")
                            message_content.set_visibility(True)
                            image_content.set_visibility(False)
                    elif RosTopic.cls_current_topic_type == 'std_msgs/msg/String':
                        # 显示文本，隐藏图片
                        message_content.set_text(RosTopic.cls_latest_message['data'])
                        message_content.set_visibility(True)
                        image_content.set_visibility(False)
                    else:
                        # 其他类型的消息
                        message_content.set_text(f"消息类型: {RosTopic.cls_current_topic_type}\n数据: {str(RosTopic.cls_latest_message)}")
                        message_content.set_visibility(True)
                        image_content.set_visibility(False)
                else:
                    # 没有消息时，显示提示信息
                    topic_name_type.set_text('Please select topic to view')
                    message_content.set_text('')
                    message_content.set_visibility(True)
                    image_content.set_visibility(False)
            
            # 添加定时器更新消息显示
            ui.timer(1.0, update_message_display)

    with ui.left_drawer().style('background-color: #d7e3f4'):
        # 状态栏区域
        with ui.card().style('background-color: #ffffff; margin-bottom: 5px;'):
            with ui.card_section():
                ui.label('Device Status').classes('text-h6 font-bold')
                
                # 状态信息
                status_text = ui.label('N/A').classes('text-body1')
                ros_host_label = ui.label('N/A').classes('text-body2')
                update_time_label = ui.label('N/A').classes('text-body2 text-grey')

                def update_status_display():
                    """更新状态栏显示"""
                    # 使用控制器获取和格式化状态
                    status = device_controller.get_connection_status()

                    # 更新UI标签
                    status_text.set_text(f"ROS Server: {status['is_connected']}")
                    ros_host_label.set_text(f"Ros Bridge:{status['ros_host']}:{status['ros_port']}")
                    update_time_label.set_text(status['update_time'])

        
        # Connect to device
        with ui.column():
            device_ip_input = ui.input(label='Device IP', placeholder='localhost', value='localhost')
            
            def handle_connect_click():
                """处理连接按钮点击"""
                ip = device_ip_input.value
                
                # 使用控制器处理连接逻辑
                device_controller.connect_to_device(ip)

                # 更新状态栏
                update_status_display()
            
            # 连接按钮
            ui.button(text='Connect', on_click=handle_connect_click)
        
        # Topic process
        with ui.column():
            ui.label('ROS Topics').classes('text-h6 font-bold mt-6')
            
            # Topic列表容器
            topic_list_item = ui.dropdown_button("Select Topic", auto_close=True)
            
            def refresh_topics():
                """刷新topic列表"""
                # 清空下拉菜单
                topic_list_item.clear()
                
                # 获取最新的topic列表
                topic_list = bridge_controller.get_all_topics()
                logging.info(f"刷新topic列表，获取到 {len(topic_list)} 个topics")
                
                # 添加topic项到下拉菜单
                with topic_list_item:
                    for topic in topic_list:
                        topic_name = topic['name']
                        ui.item(topic_name, on_click=lambda t=topic: handle_topic_click(t))
            
            # 设置点击事件，点击下拉按钮时刷新topic列表
            topic_list_item.on_click(refresh_topics)
    
    def update_timer():
        # 定时更新状态栏
        ui.timer(5.0, update_status_display)
    
    update_timer()
