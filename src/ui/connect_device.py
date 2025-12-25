from nicegui import ui
from ui_function.connect_device_controller import ConnectDeviceController
from ui_function.topic_controller import TopicController

@ui.page('/connect_device_page')
def connect_device_page():
    ui.page_title('Qualcomm Robotics SDK Tools')
    
    # 创建控制器实例
    device_controller = ConnectDeviceController()
    topic_controller = TopicController()
    
    # 存储当前选中的topic数据
    selected_topic_data = {'name': None, 'type': None, 'messages': []}
    
    with ui.header(elevated=True).style('background-color: #4f6db9'):
        ui.link('Qualcomm Robotics SDK', '/').classes('text-red-500')
        ui.link('Connect device', '/connect_device_page').classes('text-red-500')
        ui.link('Topic', '/topic_page').classes('text-red-500')
    
    with ui.left_drawer().style('background-color: #d7e3f4'):
        # 状态栏区域
        with ui.card().style('background-color: #ffffff; margin-bottom: 5px;'):
            with ui.card_section():
                ui.label('连接状态').classes('text-h6 font-bold')
                
                # 状态指示器
                status_text = ui.label('状态: 检查中...').classes('text-body1')
                
                # 状态信息
                device_ip_label = ui.label('设备IP: -').classes('text-body2')
                ros_host_label = ui.label('ROS主机: -').classes('text-body2')
                update_time_label = ui.label('更新时间: -').classes('text-body2 text-grey')
        
        # 功能区域
        with ui.column():
            device_ip_input = ui.input(label='Device IP', placeholder='localhost', value='localhost')
            
            # 创建消息标签（放在按钮下面）
            message_label = ui.label('').classes('text-lg mt-4')
            
            def update_status_display():
                """更新状态栏显示"""
                # 使用控制器获取和格式化状态
                status = device_controller.get_connection_status()
                formatted = device_controller.format_status_text(status)
                
                # 更新UI标签
                status_text.set_text(formatted['status_text'])
                device_ip_label.set_text(formatted['device_ip_text'])
                ros_host_label.set_text(formatted['ros_host_text'])
                update_time_label.set_text(formatted['update_time_text'])
            
            def handle_connect_click():
                """处理连接按钮点击"""
                ip = device_ip_input.value
                
                # 使用控制器处理连接逻辑
                success, message = device_controller.connect_to_device(ip)
                
                # 设置消息颜色
                if success:
                    message_label.classes('text-green-500', remove='text-red-500 text-blue-500')
                else:
                    message_label.classes('text-red-500', remove='text-green-500 text-blue-500')
                
                # 显示消息
                message_label.set_text(message)
                
                # 更新状态栏显示
                update_status_display()
                
                # 连接后更新topic列表
                update_topic_display()
            
            # 初始更新状态栏
            update_status_display()
            
            # 连接按钮
            ui.button(text='Connect', on_click=handle_connect_click)
            
            # ROS Topic列表区域（放在connect button下方）
            ui.label('ROS Topics').classes('text-h6 font-bold mt-6')
            
            # Topic连接状态
            topic_status = ui.label('Topic状态: 检查中...').classes('text-body2 mb-2')
            
            # Topic列表容器 - 可滚动区域
            topic_list_container = ui.column().classes('w-full max-h-80 overflow-y-auto border rounded p-2')
            
            def handle_topic_click(topic_name: str, topic_type: str):
                """处理topic点击事件"""
                selected_topic_data['name'] = topic_name
                selected_topic_data['type'] = topic_type
                selected_topic_data['messages'] = [f"点击时间: {ui.time().strftime('%H:%M:%S')}"]
                
                # 更新数据展示区域
                update_topic_data_display()
            
            def update_topic_display():
                """更新ROS topic列表显示"""
                # 获取topic状态
                topic_status_info = topic_controller.get_topic_status()
                topic_status.set_text(topic_status_info['message'])
                topic_status.classes(topic_status_info['status_class'], remove='text-green-500 text-red-500')
                
                # 清空当前列表
                topic_list_container.clear()
                
                if topic_controller.ros_bridge.ros_is_connected:
                    # 获取所有topic
                    topics = topic_controller.get_all_topics()
                    formatted = topic_controller.format_topic_display(topics)
                    
                    if formatted['has_topics']:
                        # 显示topic数量
                        with topic_list_container:
                            ui.label(formatted['message']).classes('text-caption text-gray-600 mb-2 font-bold')
                        
                        # 显示所有topic，每个都有点击事件
                        for topic in formatted['topics']:
                            with topic_list_container:
                                # 使用div代替card，添加点击事件
                                with ui.element('div').classes('w-full mb-2 p-3 border rounded hover:bg-blue-50 cursor-pointer transition-colors').on('click', lambda t=topic: handle_topic_click(t['name'], t['type'])):
                                    # Topic名称
                                    ui.label(topic['display_name']).classes('text-sm font-bold truncate')
                                    
                                    # Topic类型
                                    with ui.row().classes('items-center mt-1'):
                                        ui.icon('category').classes('text-gray-400 mr-1')
                                        ui.label(topic['display_type']).classes('text-xs text-gray-600')
                    else:
                        with topic_list_container:
                            ui.label(formatted['message']).classes('text-caption text-gray-500 italic')
                else:
                    with topic_list_container:
                        ui.label('请先连接到ROS以查看topic列表').classes('text-caption text-gray-500 italic')
            
            # 控制按钮区域
            with ui.row().classes('w-full mt-3 justify-between'):
                ui.button('刷新列表', on_click=update_topic_display, icon='refresh').classes('text-sm')
                ui.button('清空列表', on_click=lambda: topic_list_container.clear(), icon='clear').classes('text-sm')
            
            # 初始更新topic列表
            update_topic_display()
    
    # 主内容区域 - 用于显示选中的topic数据
    with ui.column().classes('ml-80 p-8 w-full'):
        ui.label('Topic数据展示').classes('text-h5 font-bold mb-6')
        
        # 数据展示容器
        data_display_container = ui.column().classes('w-full border rounded-lg p-6 bg-white shadow-sm')
        
        def update_topic_data_display():
            """更新topic数据展示"""
            data_display_container.clear()
            
            with data_display_container:
                if selected_topic_data['name']:
                    # 显示选中的topic信息
                    ui.label(f'当前选中的Topic: {selected_topic_data["name"]}').classes('text-h6 font-bold text-blue-600 mb-4')
                    
                    with ui.card().classes('w-full mb-4'):
                        with ui.card_section():
                            with ui.grid(columns=2).classes('w-full gap-4'):
                                ui.label('Topic名称:').classes('font-bold')
                                ui.label(selected_topic_data['name']).classes('text-gray-700')
                                
                                ui.label('Topic类型:').classes('font-bold')
                                ui.label(selected_topic_data['type']).classes('text-gray-700')
                    
                    # 数据消息区域
                    ui.label('数据消息:').classes('text-h6 font-bold mt-6 mb-3')
                    
                    if selected_topic_data['messages']:
                        for msg in selected_topic_data['messages']:
                            with ui.card().tight().classes('w-full mb-2 bg-gray-50'):
                                with ui.card_section().classes('p-3'):
                                    ui.label(msg).classes('text-sm')
                    else:
                        ui.label('暂无数据消息').classes('text-gray-500 italic')
                    
                    # 模拟数据按钮
                    def add_mock_data():
                        import datetime
                        new_msg = f"模拟数据 [{datetime.datetime.now().strftime('%H:%M:%S')}]: 这是 {selected_topic_data['name']} 的测试数据"
                        selected_topic_data['messages'].append(new_msg)
                        update_topic_data_display()
                    
                    ui.button('添加模拟数据', on_click=add_mock_data, icon='add').classes('mt-4')
                else:
                    ui.label('请点击左侧的topic以查看数据').classes('text-gray-500 italic text-center py-8')
                    ui.icon('touch_app').classes('text-4xl text-gray-300 mx-auto mt-4')
        
        # 初始显示
        update_topic_data_display()
    
    # 定时更新状态栏
    ui.timer(5.0, update_status_display)
    
    # 定时更新topic列表（频率较低，避免频繁请求）
    ui.timer(10.0, update_topic_display)
